# storage/database.py
import json
import sqlite3
from datetime import datetime, timedelta

DB_PATH = "events.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Tạo bảng events nếu chưa có.
    Đảm bảo luôn có cột color.
    """
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS events(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event TEXT,
            start_time TEXT,
            end_time TEXT,
            location TEXT,
            reminder_minutes INTEGER
        )
        """
    )
    conn.commit()

    # Đảm bảo có cột color
    c.execute("PRAGMA table_info(events)")
    columns = [row["name"] for row in c.fetchall()]
    if "color" not in columns:
        try:
            c.execute("ALTER TABLE events ADD COLUMN color TEXT")
            conn.commit()
        except sqlite3.OperationalError:
            # Có thể do column đã tồn tại -> bỏ qua
            pass

    conn.close()

def init_settings():
    conn = sqlite3.connect("events.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS settings(
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_setting(key, value):
    conn = sqlite3.connect("events.db")
    c = conn.cursor()
    c.execute("REPLACE INTO settings(key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()

def load_settings():
    conn = sqlite3.connect("events.db")
    c = conn.cursor()
    c.execute("SELECT key, value FROM settings")
    rows = c.fetchall()
    conn.close()
    return {k: json.loads(v) for k, v in rows}


def row_to_dict(row: sqlite3.Row):
    """
    Chuyển 1 dòng Row của sqlite thành dict chuẩn dùng cho API/UI.
    """
    if row is None:
        return None

    # row.keys() trả về danh sách tên cột
    cols = row.keys()
    return {
        "id": row["id"],
        "event": row["event"],
        "start_time": row["start_time"],
        "end_time": row["end_time"],
        "location": row["location"],
        "reminder_minutes": row["reminder_minutes"],
        "color": row["color"] if "color" in cols else None,
    }


# =============================
# CRUD CƠ BẢN
# =============================


def list_events():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM events ORDER BY start_time")
    rows = c.fetchall()
    conn.close()
    return [row_to_dict(r) for r in rows]


def get_event(event_id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM events WHERE id = ?", (event_id,))
    row = c.fetchone()
    conn.close()
    return row_to_dict(row) if row else None


def save_event_to_db(data: dict):
    """
    Thêm mới 1 event.
    data: {event, start_time, end_time, location, reminder_minutes, color}
    """
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        """
        INSERT INTO events(event, start_time, end_time, location, reminder_minutes, color)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            data.get("event"),
            data.get("start_time"),
            data.get("end_time"),
            data.get("location"),
            data.get("reminder_minutes", 0),
            data.get("color", "#22c55e"),
        ),
    )
    conn.commit()
    conn.close()


def update_event(event_id: int, data: dict):
    """
    Cập nhật event theo id.
    """
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        """
        UPDATE events
        SET event = ?, start_time = ?, end_time = ?, location = ?, reminder_minutes = ?, color = ?
        WHERE id = ?
        """,
        (
            data.get("event"),
            data.get("start_time"),
            data.get("end_time"),
            data.get("location"),
            data.get("reminder_minutes", 0),
            data.get("color", "#22c55e"),
            event_id,
        ),
    )
    conn.commit()
    conn.close()


def delete_event(event_id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM events WHERE id = ?", (event_id,))
    conn.commit()
    conn.close()


def search_events(keyword: str):
    """
    Tìm theo tên sự kiện hoặc location (LIKE %keyword% – không phân biệt hoa thường)
    """
    kw = f"%{keyword.lower()}%"
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        """
        SELECT * FROM events
        WHERE LOWER(event) LIKE ? OR LOWER(location) LIKE ?
        ORDER BY start_time
        """,
        (kw, kw),
    )
    rows = c.fetchall()
    conn.close()
    return [row_to_dict(r) for r in rows]


# =============================
# TRUY VẤN THEO THÁNG / THỐNG KÊ
# =============================


def get_events_for_month(year: int, month: int):
    events = list_events()
    result = []
    for ev in events:
        st = ev["start_time"]
        if not st:
            continue
        try:
            dt = datetime.fromisoformat(st)
        except Exception:
            continue
        if dt.year == year and dt.month == month:
            ev["date_str"] = dt.date().isoformat()
            ev["day"] = dt.day
            ev["time_str"] = dt.strftime("%H:%M")
            result.append(ev)
    return result


def get_stats_for_month(year: int, month: int):
    events = get_events_for_month(year, month)
    per_day = {}
    per_week = {}

    for ev in events:
        dt = datetime.fromisoformat(ev["start_time"])
        dkey = dt.date().isoformat()
        per_day[dkey] = per_day.get(dkey, 0) + 1

        iso_year, iso_week, _ = dt.isocalendar()
        wkey = f"{iso_year}-W{iso_week:02d}"
        per_week[wkey] = per_week.get(wkey, 0) + 1

    return {
        "total_events": len(events),
        "by_day": per_day,
        "by_week": per_week,
    }
