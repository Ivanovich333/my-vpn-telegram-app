import requests
import urllib3
import json
import random
import uuid
import time
import base64
import os

from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives import serialization
from dotenv import load_dotenv 

# Отключаем предупреждения об отсутствии проверки SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


load_dotenv()

BASE_URL = str(os.getenv('BASE_URL_VLESS'))
USERNAME = str(os.getenv('USERNAME_VLESS'))
PASSWORD = str(os.getenv('PASSWORD_VLESS'))

# Настройки
#BASE_URL = 'https://216.173.69.109:52228/pivopivopivokvas228'  # Ваш реальный URL
#USERNAME = 'f2005pro'  # Ваше имя пользователя
#PASSWORD = 'davidsoso228'  # Ваш пароль

print(BASE_URL, USERNAME, PASSWORD)

# Создаем сессию
session = requests.Session()


def generate_reality_keys():
    """Генерирует пару ключей для протокола Reality, закодированных в URL-safe base64 без символов заполнения."""
    private_key = x25519.X25519PrivateKey.generate()
    public_key = private_key.public_key()
    
    # Получаем байты приватного ключа
    private_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    # Получаем байты публичного ключа
    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )
    
    # Кодируем ключи в URL-safe base64 без символов заполнения
    private_key_b64 = base64.urlsafe_b64encode(private_bytes).rstrip(b'=').decode('utf-8')
    public_key_b64 = base64.urlsafe_b64encode(public_bytes).rstrip(b'=').decode('utf-8')
    
    # Проверяем длину ключей (должна быть 43 символа для 32-байтового ключа без заполнения)
    assert len(private_key_b64) == 43, f"Неправильная длина приватного ключа: {len(private_key_b64)} символов"
    assert len(public_key_b64) == 43, f"Неправильная длина публичного ключа: {len(public_key_b64)} символов"
    
    return private_key_b64, public_key_b64

def login():
    login_url = f'{BASE_URL}/login'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    payload = {
        'username': USERNAME,
        'password': PASSWORD
    }
    response = session.post(login_url, json=payload, headers=headers, verify=False)
    if response.status_code == 200:
        print('Успешно аутентифицированы')
        return True
    else:
        print('Ошибка аутентификации')
        print(response.text)
        return False

def get_inbounds():
    url = f'{BASE_URL}/panel/api/inbounds/list'
    response = session.get(url, verify=False)
    if response.status_code == 200:
        data = response.json()
        print('Доступные inbound\'ы:')
        for inbound in data.get('obj', []):
            print(f"ID: {inbound['id']}, Remark: {inbound['remark']}")
    else:
        print('Ошибка при получении списка inbound\'ов')
        print(response.text)
    
def create_inbound(tg_user_ID = 'CHANGE', port = 12351, ip_address = None, email = None, username = None):

    url = f'{BASE_URL}/panel/api/inbounds/add'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    tg_full_id = str(tg_user_ID) + '*' + str(email)
    # Генерация случайных параметров
    private_key, public_key = generate_reality_keys()

    dest = "google.com:443"
    server_names = ["google.com", "www.google.com"]  # Используем список serverNames
    
    # Генерация клиента
    client_id = str(uuid.uuid4())

    sub_id = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=16))
    client_email = f'{sub_id}@pin5632.tg'
    
    settings = {
        "clients": [
            {
                "id": client_id,
                "flow": "",
                "email": client_email,
                "limitIp": 0,
                "totalGB": 0,
                "expiryTime": 0,
                "enable": True,
                "tgId": "",
                "subId": sub_id,
                "reset": 0
            }
        ],
        "decryption": "none",
        "fallbacks": []
    }
    
    stream_settings = {
        "network": "tcp",
        "security": "reality",
        "externalProxy": [],
        "realitySettings": {
            "show": False,
            "xver": 0,
            "dest": dest,
            "serverNames": server_names,
            "privateKey": private_key,
            "minClient": "",
            "maxClient": "",
            "maxTimediff": 0,
            "shortIds": [
                ''.join(random.choices('abcdef0123456789', k=8)),
                ''.join(random.choices('abcdef0123456789', k=16)),
                ''.join(random.choices('abcdef0123456789', k=2)),
                ''.join(random.choices('abcdef0123456789', k=6)),
                ''.join(random.choices('abcdef0123456789', k=12)),
                ''.join(random.choices('abcdef0123456789', k=12)),
                ''.join(random.choices('abcdef0123456789', k=8)),
                ''.join(random.choices('abcdef0123456789', k=4))
            ],
            "settings": {
                "publicKey": public_key,
                "fingerprint": "random",
                "serverName": "",
                "spiderX": "/"
            }
        },
        "tcpSettings": {
            "acceptProxyProtocol": False,
            "header": {
                "type": "none"
            }
        }
    }
    
    sniffing = {
        "enabled": True,
        "destOverride": ["http", "tls", "quic", "fakedns"],
        "metadataOnly": False,
        "routeOnly": False
    }
    
    allocate = {
        "strategy": "always",
        "refresh": 5,
        "concurrency": 3
    }
    
    tag = f"inbound-{port}"
    
    payload = {
        "remark": tg_full_id,
        "port": port,
        "protocol": "vless",
        "settings": json.dumps(settings, ensure_ascii=False),
        "streamSettings": json.dumps(stream_settings, ensure_ascii=False),
        "sniffing": json.dumps(sniffing, ensure_ascii=False),
        "allocate": json.dumps(allocate, ensure_ascii=False),
        "tag": tag,
        "enable": True
    }
    
    client_id = settings["clients"][0]["id"]
    ip_address = ip_address  # Замените на нужный IP адрес
    port = port  # Укажите нужный порт
    stream_network = stream_settings["network"]
    security = stream_settings["security"]
    public_key = stream_settings["realitySettings"]["settings"]["publicKey"]
    fp = stream_settings["realitySettings"]["settings"]["fingerprint"]
    sni = server_names[0]  # Замените на нужный SNI
    sid = stream_settings['realitySettings']['shortIds'][0]  # Замените на нужный SID
    spx = "%2F"  # Замените на нужный SPX
    tg_user_ID = tg_user_ID  # Замените на нужный TG User ID

    # Для отладки: выводим payload перед отправкой
    print("Payload для создания inbound:")
    print(json.dumps(payload, indent=4, ensure_ascii=False))
    
    key_vless = f"vless://{client_id}@{ip_address}:{port}?type={stream_network}&security={security}&pbk={public_key}&fp={fp}&sni={sni}&sid={sid}&spx={spx}#{tg_user_ID}-{client_email}"
    print("--------------------------------")
    print(key_vless)
    
    response = session.post(url, json=payload, headers=headers, verify=False)
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            inbound_id = data.get('obj', {}).get('id')
            print('Inbound успешно создан')
            print(f"ID нового inbound: {inbound_id}")
            return inbound_id, key_vless
        else:
            print('Ошибка при создании inbound1')
            print(data.get('msg'))
            return None
    else:
        print('Ошибка при создании inbound2')
        print(response.text)
        return None

def add_client(inbound_id):
    url = f'{BASE_URL}/panel/api/inbounds/addClient'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    # Генерация информации о клиенте
    client_id = str(uuid.uuid4())
    email = f'client_{client_id[:8]}@pin5632.com'
    expiry_time = int(time.time() * 1000) + (30 * 24 * 60 * 60 * 1000)  # 30 дней в миллисекундах

    settings = {
        "clients": [{
            "id": client_id,
            "alterId": 0,
            "email": email,
            "limitIp": 2,
            "totalGB": 10000000000000000,
            "expiryTime": expiry_time,
            "enable": True,
            "tgId": "",
            "subId": ""
        }]
    }

    payload = {
        "id": inbound_id,
        "settings": json.dumps(settings, ensure_ascii=False)
    }

    # Для отладки: выводим payload перед отправкой
    print("Payload для добавления клиента:")
    print(json.dumps(payload, indent=4, ensure_ascii=False))

    response = session.post(url, json=payload, headers=headers, verify=False)
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print(f'Client успешно добавлен: {email}')
        else:
            print('Ошибка при добавлении клиента')
            print(data.get('msg'))
    else:
        print('Ошибка при добавлении клиента')
        print(response.text)

def get_inbound():
    data_users = []
    url = f'{BASE_URL}/panel/api/inbounds/list'
    response = session.get(url, verify=False)
    
    if response.status_code == 200:
        data = response.json()
        print('Доступные inbound\'ы:')
        
        for inbound in data.get('obj', []):
            total_inf = inbound['up'] + inbound['down']
            print(f"ID: {inbound['id']}, Remark: {inbound['remark']}, Up: {inbound['up']}, Down: {inbound['down']}, Total: {total_inf}")
            # Добавляем информацию о каждом inbound в список
            data_users.append([inbound['id'], inbound['remark'], inbound['up'], inbound['down']])
    
    else:
        print('Ошибка при получении списка inbound\'ов')
        print(response.text)

    return data_users

if __name__ == '__main__':
 
    if login():
        get_inbounds()
        inbound_id = create_inbound()
        if inbound_id:
            # Если клиент добавляется при создании inbound, следующая строка не нужна
            # add_client(inbound_id)
            a = get_inbound()
            print(a)
