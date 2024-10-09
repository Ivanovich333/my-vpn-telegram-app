import requests
import urllib3
import json

# Отключаем предупреждения об отсутствии проверки SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Настройки
BASE_URL = 'https://216.173.69.109:52228/pivopivopivokvas228'  # Ваш реальный URL
USERNAME = 'f2005pro'  # Ваше имя пользователя
PASSWORD = 'davidsoso228'  # Ваш пароль

# Создаем сессию
session = requests.Session()

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

def get_client_info(email):
    url = f'{BASE_URL}/panel/api/inbounds/getClientTraffics/{email}'
    headers = {
        'Accept': 'application/json'
    }
    response = session.get(url, headers=headers, verify=False)
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            client_info = data.get('obj')
            return client_info
        else:
            print(f"Не удалось получить информацию о клиенте: {data.get('msg')}")
            return None
    else:
        print(f"Ошибка при получении информации о клиенте: {response.status_code}")
        print(response.text)
        return None

def get_client_uuid(inbound_id, email):
    url = f'{BASE_URL}/panel/api/inbounds/get/{inbound_id}'
    headers = {
        'Accept': 'application/json'
    }
    response = session.get(url, headers=headers, verify=False)
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            inbound_obj = data.get('obj')
            settings = inbound_obj.get('settings')
            settings_json = json.loads(settings)
            clients = settings_json.get('clients', [])
            # Находим клиента с нужным email
            for client in clients:
                if client.get('email') == email:
                    return client.get('id')
            print('Клиент с указанным email не найден в inbound')
            return None
        else:
            print(f"Не удалось получить информацию об inbound: {data.get('msg')}")
            return None
    else:
        print(f"Ошибка при получении информации об inbound: {response.status_code}")
        print(response.text)
        return None

def delete_client(inbound_id, client_uuid):
    url = f'{BASE_URL}/panel/api/inbounds/{inbound_id}/delClient/{client_uuid}'
    headers = {
        'Accept': 'application/json'
    }
    response = session.post(url, headers=headers, verify=False)
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print('Клиент успешно удален')
        else:
            print(f"Не удалось удалить клиента: {data.get('msg')}")
    else:
        print(f"Ошибка при удалении клиента: {response.status_code}")
        print(response.text)

if __name__ == '__main__':
    if login():
        email_to_delete = 'yg2yj5qw'  # Замените на email пользователя, которого нужно удалить
        client_info = get_client_info(email_to_delete)
        if client_info:
            inbound_id = client_info.get('inboundId')
            client_uuid = get_client_uuid(inbound_id, email_to_delete)
            if client_uuid:
                delete_client(inbound_id, client_uuid)
            else:
                print('UUID клиента не найден')
        else:
            print('Клиент не найден')
