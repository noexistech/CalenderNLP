# storage/database.py
import sqlite3

def init_db():
    conn = sqlite3.connect("events.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS events(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event TEXT,
            start_time TEXT,
            end_time TEXT,
            location TEXT,
            reminder_minutes INTEGER
        )
    """)
    conn.commit()
    conn.close()


def save_event(data):
    conn = sqlite3.connect("events.db")
    c = conn.cursor()
    c.execute("""
        INSERT INTO events(event,start_time,end_time,location,reminder_minutes)
        VALUES (?,?,?,?,?)
    """, (data["event"], data["start_time"], data["end_time"], data["location"], data["reminder_minutes"]))
    conn.commit()
    conn.close()
