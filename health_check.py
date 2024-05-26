import os
import time
import requests
from deta import Deta
from dotenv import load_dotenv

# Load environment variables from Github Secrets
DETA_PROJECT_KEY = os.getenv('DETA_PROJECT_KEY')
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')

# Deta Base setup
deta = Deta(DETA_PROJECT_KEY)
db = deta.Base('server_health')

def fetch_url():
    response = requests.get('http://93days.me')
    status_code = response.status_code
    response_time = response.elapsed.total_seconds()
    data = {
        'timestamp': time.time(),
        'status_code': status_code,
        'response_time': response_time
    }
    db.put(data)
    if status_code == 200 and response_time < 3:
        print(f'The status code: {status_code}, Response time: {response_time}')
    else:
        print(f'Huston, we are in trouble!')
        send_alert(f'Problem detected! Status code: {status_code}, Response time: {response_time}')

def send_alert(message):
    payload = {
        'content': message
    }
    response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
    if response.status_code != 204:
        print(f'Failed to send alert: {response.status_code}, {response.text}')

fetch_url()