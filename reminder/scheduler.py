# reminder/scheduler.py
import threading, time
from datetime import datetime
import sqlite3

def reminder_loop():
    while True:
        conn = sqlite3.connect("events.db")
        c = conn.cursor()

        c.execute("SELECT event, start_time, reminder_minutes FROM events")
        rows = c.fetchall()
        conn.close()

        now = datetime.now()

        for event, start_time, reminder in rows:
            dt = datetime.fromisoformat(start_time)
            diff = (dt - now).total_seconds()

            if 0 < diff <= reminder * 60:
                print(f"🔔 Nhắc nhở: Sự kiện '{event}' sẽ diễn ra lúc {start_time}")

        time.sleep(60)  # kiểm tra mỗi phút


def start_scheduler():
    thread = threading.Thread(target=reminder_loop, daemon=True)
    thread.start()
