import os
import time
import requests
from deta import Deta

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
    
    if status_code == 200 or status_code == 204:
        if response_time > 3:
            message = f":yellow_square: Status Code: {status_code} with Response Time {response_time:.2f}s. Not meet the standard server health (above 3s)."
            send_alert(message)
    else:
        message = f":red_square: Huston we've problem! Status Code {status_code} - Response Time {response_time:.2f}s. Website couldn't be reach. Kindly check and monitor if the problem persist."
        send_alert(message)
    
    print(f'Status code: {status_code}, Response time: {response_time:.2f}s')

def send_alert(message):
    payload = {
        'content': message
    }
    response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
    if response.status_code != 204:
        print(f'Failed to send alert: {response.status_code}, {response.text}')

if __name__ == "__main__":
    fetch_url()