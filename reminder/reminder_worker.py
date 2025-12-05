# reminder/reminder_worker.py
import time
import requests

API_URL = "http://127.0.0.1:5000/api/check_reminder"

while True:
    try:
        resp = requests.get(API_URL).json()
        for e in resp:
            print(f"[REMINDER] Sắp diễn ra: {e['event']} lúc {e['start_time']} tại {e['location']}")
    except:
        pass

    time.sleep(60)
