# bot.py
import asyncio
import os
import logging
import sqlite3
import json
import re
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

# Load environment variables (ensure thcoese are set in your environment)
HOST = os.getenv('SSH_HOST')
USERNAME = os.getenv('SSH_USERNAME')
PASSWORD = os.getenv('SSH_PASSWORD')
SERVER_API_URL = os.getenv('SERVER_API_URL')  # e.g., 'https://216.173.69.109:49744/eR6p5QhdXM2pMUD6pAB_Rw'
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ADMIN_IDS = json.loads(os.getenv('ADMIN_IDS', '[]'))  # e.g., '[554164909, 5215786730]'
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
            Outline_keys TEXT DEFAULT '[]'
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

# Save user to the database
def save_user(user, payment_info='FALSE', VLESS_keys=None, Outline_keys=None):
    if VLESS_keys is None:
        VLESS_keys = []
    if Outline_keys is None:
        Outline_keys = []

    VLESS_keys_json = json.dumps(VLESS_keys)
    Outline_keys_json = json.dumps(Outline_keys)

    conn = connect_db()
    if conn is None:
        return
    cursor = conn.cursor()

    try:
        cursor.execute('''
            INSERT OR IGNORE INTO users (
                user_id, first_name, last_name, username, payment_info, VLESS_keys, Outline_keys
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            user.id, user.first_name, user.last_name, user.username, payment_info, VLESS_keys_json, Outline_keys_json
        ))
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
        ssh.close()
        return result
    except Exception as e:
        logging.error(f"SSH command error: {e}")
        return None

def new_outline_key():
    command = f'curl --insecure -X POST {SERVER_API_URL}/access-keys'
    output = run_ssh_command(command)
    if output:
        try:
            data = json.loads(output)
            key_id = data.get('id')
            access_url = data.get('accessUrl')
            return key_id, access_url
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding JSON: {e}")
    return None, None

def delete_outline_key(key_id):
    command = f'curl --insecure -X DELETE {SERVER_API_URL}/access-keys/{key_id}'
    output = run_ssh_command(command)
    return output

def add_outline_key_to_user(user_id, key_id, key_url):
    conn = connect_db()
    if conn is None:
        return
    cursor = conn.cursor()

    try:
        cursor.execute('UPDATE users SET Outline_keys = ?, payment_info = ? WHERE user_id = ?', (json.dumps([key_url]), 'TRUE', user_id))
        conn.commit()
    except sqlite3.Error as e:
        logging.error(f"Error updating user with new key: {e}")
    finally:
        conn.close()

def get_user_outline_key(user_id):
    conn = connect_db()
    if conn is None:
        return None
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT Outline_keys FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        if result:
            keys = json.loads(result[0])
            return keys[0] if keys else None
    except sqlite3.Error as e:
        logging.error(f"Error retrieving user key: {e}")
    finally:
        conn.close()
    return None

def remove_user_outline_key(user_id):
    conn = connect_db()
    if conn is None:
        return
    cursor = conn.cursor()

    try:
        cursor.execute('UPDATE users SET Outline_keys = ?, payment_info = ? WHERE user_id = ?', ('[]', 'FALSE', user_id))
        conn.commit()
    except sqlite3.Error as e:
        logging.error(f"Error removing user key: {e}")
    finally:
        conn.close()

from telegram.ext import ContextTypes

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

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
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
        await query.message.reply_text('Select the required key:', reply_markup=keys_keyboard())

    elif query.data == 'outline_key':
        existing_key = get_user_outline_key(user_id)
        if existing_key:
            await query.message.reply_text(
                f'Your existing key:\n`{existing_key}`\nDo you want to update it?',
                parse_mode='Markdown',
                reply_markup=outline_update_keyboard()
            )
        else:
            key_id, key_url = new_outline_key()
            if key_id and key_url:
                add_outline_key_to_user(user_id, key_id, key_url)
                await query.message.reply_text(
                    f'Your new key:\n`{key_url}`',
                    parse_mode='Markdown',
                    reply_markup=return_keyboard()
                )
            else:
                await query.message.reply_text('Failed to generate new key.', reply_markup=return_keyboard())

    elif query.data == 'outline_update':
        existing_key = get_user_outline_key(user_id)
        if existing_key:
            # Extract key ID from the existing key URL
            key_id = extract_key_id(existing_key)
            delete_outline_key(key_id)
            remove_user_outline_key(user_id)
        key_id, key_url = new_outline_key()
        if key_id and key_url:
            add_outline_key_to_user(user_id, key_id, key_url)
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

# Function to extract key ID from the key URL
def extract_key_id(key_url):
    # Implement extraction logic based on your key URL structure
    # Example placeholder implementation:
    return key_url.split('/')[-1]

def main():
    create_tables()

    # Ensure environment variables are set
    if not all([HOST, USERNAME, PASSWORD, SERVER_API_URL, BOT_TOKEN]):
        logging.error('Environment variables are not properly set.')
        return

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Command handlers
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('admin', admin))

    # Message handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Callback query handler
    app.add_handler(CallbackQueryHandler(button_handler))

    # Run the bot
    app.run_polling()

if __name__ == '__main__':
    main()
