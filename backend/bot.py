# bot.py
import asyncio
import os
import logging
import sqlite3
import json
import threading
from dotenv import load_dotenv  # Import load_dotenv from python-dotenv

from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo,
)
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
import paramiko  # Be cautious with this in async environments

load_dotenv()

# Load environment variables
HOST = os.getenv('SSH_HOST')
USERNAME = os.getenv('SSH_USERNAME')
PASSWORD = os.getenv('SSH_PASSWORD')
SERVER_API_URL = os.getenv('SERVER_API_URL')
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ADMIN_IDS = json.loads(os.getenv('ADMIN_IDS', '[]'))
WEB_APP_URL = os.getenv('WEB_APP_URL', 'https://myvpn123.netlify.app/')

# Logging configuration
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Database connection
def connect_db():
    try:
        conn = sqlite3.connect('users.db')
        return conn
    except sqlite3.Error as e:
        logging.error(f"Database connection error: {e}")
        return None

# Create tables if they don't exist
def create_tables():
    conn = connect_db()
    if conn is None:
        return
    cursor = conn.cursor()

    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE,
            first_name TEXT,
            last_name TEXT,
            username TEXT,
            payment_info TEXT DEFAULT 'FALSE',
            VLESS_keys TEXT DEFAULT '[]',
            Outline_key_id TEXT,
            Outline_key_url TEXT
        )
    ''')

    # Create messages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    conn.commit()
    conn.close()

# Save or update user in the database
def save_user(user, payment_info=None, VLESS_keys=None, Outline_key_id=None, Outline_key_url=None):
    conn = connect_db()
    if conn is None:
        return
    cursor = conn.cursor()

    try:
        # Build the columns and values dynamically
        columns = ['user_id', 'first_name', 'last_name', 'username']
        values = [user.id, user.first_name, user.last_name, user.username]

        if payment_info is not None:
            columns.append('payment_info')
            values.append(payment_info)

        if VLESS_keys is not None:
            columns.append('VLESS_keys')
            values.append(json.dumps(VLESS_keys))

        if Outline_key_id is not None:
            columns.append('Outline_key_id')
            values.append(Outline_key_id)

        if Outline_key_url is not None:
            columns.append('Outline_key_url')
            values.append(Outline_key_url)

        placeholders = ', '.join(['?'] * len(values))
        columns_str = ', '.join(columns)
        update_str = ', '.join([f'{col}=excluded.{col}' for col in columns if col != 'user_id'])

        sql = f'''
            INSERT INTO users ({columns_str})
            VALUES ({placeholders})
            ON CONFLICT(user_id) DO UPDATE SET {update_str}
        '''

        cursor.execute(sql, values)
        conn.commit()
    except sqlite3.Error as e:
        logging.error(f"Error saving user: {e}")
    finally:
        conn.close()

# Save message to the database
def save_message(user_id, text):
    conn = connect_db()
    if conn is None:
        return
    cursor = conn.cursor()

    try:
        cursor.execute('''
            INSERT INTO messages (user_id, message) VALUES (?, ?)
        ''', (user_id, text))
        conn.commit()
    except sqlite3.Error as e:
        logging.error(f"Error saving message: {e}")
    finally:
        conn.close()

# Handle web app data
async def web_app_data_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    save_user(user)  # Added this line
    web_app_data = update.effective_message.web_app_data
    data = web_app_data.data  # The JSON string sent from the web app

    # Parse the JSON data
    try:
        data_dict = json.loads(data)
    except json.JSONDecodeError:
        await update.message.reply_text('Invalid data received.')
        return

    action = data_dict.get('action')
    if action == 'enroll':
        # Extract additional data as needed
        payment_info = data_dict.get('payment_info', 'FALSE')
        # Enroll the user into the database
        save_user(user, payment_info=payment_info)
        await update.message.reply_text('You have been enrolled successfully!')
    else:
        await update.message.reply_text('Unknown action.')

# Main menu keyboard
def main_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("Open My VPN App", web_app=WebAppInfo(url=WEB_APP_URL))
        ],
        [
            InlineKeyboardButton("Server Status", callback_data='Status'),
            InlineKeyboardButton("Generate New Key", callback_data='New_key')
        ],
        [
            InlineKeyboardButton("My Plan", callback_data='My_Plan'),
            InlineKeyboardButton("Help", callback_data='Help')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

# Return keyboard
def return_keyboard():
    keyboard = [
        [InlineKeyboardButton("Return to Main Menu", callback_data='main_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)

# Key options keyboard
def keys_keyboard():
    keyboard = [
        [InlineKeyboardButton("Outline", callback_data='outline_key')],
        [InlineKeyboardButton("VLESS", callback_data='vless_key')]  # Placeholder for VLESS
    ]
    return InlineKeyboardMarkup(keyboard)

# Outline update keyboard
def outline_update_keyboard():
    keyboard = [
        [InlineKeyboardButton("Update", callback_data='outline_update')],
        [InlineKeyboardButton("Return", callback_data='main_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)

def run_ssh_command(command):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST, username=USERNAME, password=PASSWORD)
        stdin, stdout, stderr = ssh.exec_command(command)
        result = stdout.read().decode()
        error = stderr.read().decode()
        ssh.close()
        if error:
            logging.error(f"SSH command stderr: {error}")
        return result
    except Exception as e:
        logging.error(f"SSH command error: {e}")
        return None

def new_outline_key():
    command = f'curl -s --insecure -X POST {SERVER_API_URL}/access-keys'
    output = run_ssh_command(command)
    if output:
        try:
            data = json.loads(output)
            key_id = data.get('id')
            access_url = data.get('accessUrl')
            return key_id, access_url
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding JSON: {e}")
            logging.error(f"Output was: {output}")
    return None, None

def delete_outline_key(key_id):
    command = f'curl -s --insecure -X DELETE {SERVER_API_URL}/access-keys/{key_id}'
    output = run_ssh_command(command)
    return output

def get_user_outline_key(user_id):
    conn = connect_db()
    if conn is None:
        return None, None
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT Outline_key_id, Outline_key_url FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        if result and result[1]:
            return result[0], result[1]
    except sqlite3.Error as e:
        logging.error(f"Error retrieving user key: {e}")
    finally:
        conn.close()
    return None, None

def remove_user_outline_key(user_id):
    conn = connect_db()
    if conn is None:
        return
    cursor = conn.cursor()

    try:
        cursor.execute('UPDATE users SET Outline_key_id = NULL, Outline_key_url = NULL, payment_info = ? WHERE user_id = ?', ('FALSE', user_id))
        conn.commit()
    except sqlite3.Error as e:
        logging.error(f"Error removing user key: {e}")
    finally:
        conn.close()

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    save_user(user)
    # Create an inline keyboard with a button that opens the web app
    await update.message.reply_text(
        f'Hello, {user.first_name}! Click the button below to open the app.',
        reply_markup=main_keyboard()
    )

# Admin command handler
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    if user.id in ADMIN_IDS:
        await update.message.reply_text("Admin Panel:", reply_markup=admin_keyboard())
    else:
        await update.message.reply_text("You do not have permission to use this command.")

# Admin keyboard
def admin_keyboard():
    keyboard = [
        [InlineKeyboardButton("Add Subscription", callback_data='add_subscription')],
        [InlineKeyboardButton("Remove Subscription", callback_data='remove_subscription')],
        [InlineKeyboardButton("Return", callback_data='main_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)

# Handle incoming messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text

    save_user(user)
    save_message(user.id, text)

    if context.user_data.get('action') == 'add_subscription' and user.id in ADMIN_IDS:
        target_user_id = int(text)
        update_subscription(target_user_id, 'TRUE')
        await update.message.reply_text(f'Subscription added for user {target_user_id}.')
        context.user_data['action'] = None
    elif context.user_data.get('action') == 'remove_subscription' and user.id in ADMIN_IDS:
        target_user_id = int(text)
        update_subscription(target_user_id, 'FALSE')
        await update.message.reply_text(f'Subscription removed for user {target_user_id}.')
        context.user_data['action'] = None
    else:
        await update.message.reply_text(f'Your message "{text}" was not recognized.', reply_markup=main_keyboard())

# Update subscription status
def update_subscription(user_id, status):
    conn = connect_db()
    if conn is None:
        return
    cursor = conn.cursor()

    try:
        cursor.execute('UPDATE users SET payment_info = ? WHERE user_id = ?', (status, user_id))
        conn.commit()
    except sqlite3.Error as e:
        logging.error(f"Error updating subscription: {e}")
    finally:
        conn.close()

# Button handler
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    save_user(user)  # Added this line
    user_id = user.id

    await query.answer()  # Close the button notification

    if query.data == 'main_menu':
        await query.message.reply_text('Please choose an option:', reply_markup=main_keyboard())

    elif query.data == 'Status':
        # Run SSH command in a separate thread
        async def get_status():
            loop = asyncio.get_running_loop()
            status = await loop.run_in_executor(None, run_ssh_command, 'uptime')
            if status:
                await query.message.reply_text(f'Server Status:\n{status}', reply_markup=return_keyboard())
            else:
                await query.message.reply_text('Failed to retrieve server status.', reply_markup=return_keyboard())

        # Schedule the coroutine
        context.application.create_task(get_status())

    elif query.data == 'New_key':
        existing_key_id, _ = get_user_outline_key(user_id)
        if existing_key_id:
            delete_outline_key(existing_key_id)
            remove_user_outline_key(user_id)
        key_id, key_url = new_outline_key()
        if key_id and key_url:
            save_user(user, Outline_key_id=key_id, Outline_key_url=key_url, payment_info='TRUE')
            await query.message.reply_text(
                f'Your new key has been generated:\n`{key_url}`',
                parse_mode='Markdown',
                reply_markup=return_keyboard()
            )
        else:
            await query.message.reply_text('Failed to generate new key.', reply_markup=return_keyboard())

    elif query.data == 'outline_key':
        existing_key_id, existing_key_url = get_user_outline_key(user_id)
        if existing_key_url:
            await query.message.reply_text(
                f'Your existing key:\n`{existing_key_url}`\nDo you want to update it?',
                parse_mode='Markdown',
                reply_markup=outline_update_keyboard()
            )
        else:
            key_id, key_url = new_outline_key()
            if key_id and key_url:
                save_user(user, Outline_key_id=key_id, Outline_key_url=key_url, payment_info='TRUE')
                await query.message.reply_text(
                    f'Your new key:\n`{key_url}`',
                    parse_mode='Markdown',
                    reply_markup=return_keyboard()
                )
            else:
                await query.message.reply_text('Failed to generate new key.', reply_markup=return_keyboard())

    elif query.data == 'outline_update':
        existing_key_id, _ = get_user_outline_key(user_id)
        if existing_key_id:
            delete_outline_key(existing_key_id)
            remove_user_outline_key(user_id)
        key_id, key_url = new_outline_key()
        if key_id and key_url:
            save_user(user, Outline_key_id=key_id, Outline_key_url=key_url, payment_info='TRUE')
            await query.message.reply_text(
                f'Your updated key:\n`{key_url}`',
                parse_mode='Markdown',
                reply_markup=return_keyboard()
            )
        else:
            await query.message.reply_text('Failed to update key.', reply_markup=return_keyboard())

    elif query.data == 'add_subscription' and user_id in ADMIN_IDS:
        await query.message.reply_text('Enter the user ID to add a subscription:')
        context.user_data['action'] = 'add_subscription'

    elif query.data == 'remove_subscription' and user_id in ADMIN_IDS:
        await query.message.reply_text('Enter the user ID to remove a subscription:')
        context.user_data['action'] = 'remove_subscription'

    elif query.data == 'My_Plan':
        # Handle 'My Plan' option
        await query.message.reply_text('Here are your plan details...', reply_markup=return_keyboard())

    elif query.data == 'Help':
        # Handle 'Help' option
        await query.message.reply_text('How can I assist you?', reply_markup=return_keyboard())

    else:
        await query.message.reply_text('Option not recognized.', reply_markup=return_keyboard())

def main():
    create_tables()
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('admin', admin))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_data_handler))

    # Run the bot
    app.run_polling()

if __name__ == '__main__':
    main()
