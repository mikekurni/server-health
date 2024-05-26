import os
import requests
from deta import Deta
import time

# Deta Base setup
DETA_PROJECT_KEY = os.getenv('DETA_PROJECT_KEY')
deta = Deta(DETA_PROJECT_KEY)
db = deta.Base('server_health')

# Discord webhook setup
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')

def fetch_url():
    response = requests.get('https://kimulti.kitrans.my.id/login')
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
        print(f'We are in trouble Huston')
        send_alert(f'Problem detected! Status code: {status_code}, Response time: {response_time}')

def send_alert(message):
    payload = {
        'content': message
    }
    response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
    if response.status_code != 204:
        print(f'Failed to send alert: {response.status_code}, {response.text}')

def run_health_checks(interval=300):
    while True:
        fetch_url()
        time.sleep(interval)

if __name__ == "__main__":
    run_health_checks()
