# main_ui_web.py

import json
import threading
import time
from datetime import datetime, timedelta, date

from utils.datetime_helper import parse_iso, parse_user_datetime, iso, to_local, TZ

from zoneinfo import ZoneInfo

from flask import Flask, request, jsonify, render_template

from nlp_engine import process_text
from storage.database import (
    init_settings,
    init_db,
    list_events,
    get_event,
    load_settings,
    save_event_to_db,
    save_setting,
    update_event,
    delete_event,
    search_events,
    get_events_for_month,
    get_stats_for_month,
)

TZ = ZoneInfo("Asia/Ho_Chi_Minh")

# ==============================
# REMINDER THREAD
# ==============================

REMINDER_QUEUE = []
REMINDER_SENT = set()    # (id, start_time)
REMINDER_LOCK = threading.Lock()

def debug(*args):
    print("[REMINDER DEBUG]", *args, flush=True)

def reminder_worker():
    """Thread riêng: mỗi 60s quét DB, tính sự kiện đến giờ nhắc."""
    while True:
        try:
            now = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))
            debug("===== NEW LOOP =====")
            debug("Current time:", now)

            events = list_events()
            debug("Total events fetched:", len(events))

            with REMINDER_LOCK:
                for ev in events:

                    debug("\n--- Checking event ---")
                    debug("Event ID:", ev.get("id"))
                    debug("Event title:", ev.get("event"))
                    debug("Start time:", ev.get("start_time"))
                    debug("Reminder minutes:", ev.get("reminder_minutes"))

                    st = ev.get("start_time")
                    if not st:
                        debug("-> Skipped: No start_time")
                        continue

                    rm = ev.get("reminder_minutes") or 0
                    if rm <= 0:
                        debug("-> Skipped: reminder_minutes <= 0")
                        continue
                    
                    try:
                        start_dt = datetime.fromisoformat(st)
                        if start_dt.tzinfo is None:
                            start_dt = start_dt.replace(tzinfo=TZ)
                        else:
                            start_dt = start_dt.astimezone(TZ)
                    except Exception as e:
                        debug("ERROR parsing datetime:", e)
                        continue

                    reminder_dt = start_dt - timedelta(minutes=rm)
                    diff = (now - reminder_dt).total_seconds()

                    debug("Parsed start_dt:", start_dt)
                    debug("Computed reminder_dt:", reminder_dt)
                    debug("Time diff (seconds):", diff)

                    # Check trigger window
                    if 0 <= diff <= 60:
                        key = (ev["id"], st)
                        debug("Trigger window hit! Key:", key)

                        if key not in REMINDER_SENT:
                            debug("-> New reminder! Sending.")
                            REMINDER_SENT.add(key)

                            ev["reminder_time"] = reminder_dt.isoformat()
                            ev["date_str"] = start_dt.date().isoformat()
                            ev["time_str"] = start_dt.strftime("%H:%M")

                            REMINDER_QUEUE.append(ev)
                        else:
                            debug("-> Already sent earlier, skip.")
                    else:
                        debug("-> Not in reminder window.")

        except Exception as e:
            debug("!!! ERROR in reminder_worker loop:", e)

        debug("===== SLEEP 10s =====\n")
        time.sleep(10)

def get_due_reminders():
    with REMINDER_LOCK:
        events = list(REMINDER_QUEUE)
        REMINDER_QUEUE.clear()
        return events

# ==============================
# FLASK APP
# ==============================

app = Flask(__name__)
init_db()
init_settings()

# Khởi động thread nhắc nhở
rem_thread = threading.Thread(target=reminder_worker, daemon=True)
rem_thread.start()

# ==============================
# ROUTES
# ==============================

@app.route("/")
def index():
    today = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))
    return render_template(
        "app.html",
        current_year=today.year,
        current_month=today.month
    )

@app.route("/api/events", methods=["GET", "POST"])
def api_events():
    if request.method == "GET":
        year = int(request.args.get("year", datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).year))
        month = int(request.args.get("month", datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).month))
        events = get_events_for_month(year, month)
        stats = get_stats_for_month(year, month)
        return jsonify({"events": events, "stats": stats})

    # POST: tạo event từ câu tiếng Việt
    data = request.get_json() or {}
    text = data.get("natural_text", "").strip()
    if not text:
        return jsonify({"status": "error", "message": "Thiếu natural_text"}), 400

    parsed = process_text(text)
    # thêm color mặc định
    parsed["color"] = "#22c55e"
    # Force timezone GMT+7 cho start_time / end_time

    for key in ("start_time", "end_time"):
        if parsed.get(key):
            try:
                dt = datetime.fromisoformat(parsed[key])
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=TZ)
                else:
                    dt = dt.astimezone(TZ)
                parsed[key] = dt.isoformat()
            except:
                pass

    save_event_to_db(parsed)
    return jsonify({"status": "ok", "parsed": parsed})

@app.route("/api/events/<int:event_id>", methods=["GET", "PUT", "DELETE"])
def api_event_detail(event_id):
    ev = get_event(event_id)
    if not ev:
        return jsonify({"status":"error","message":"Not found"}), 404

    if request.method == "GET":
        st = ev.get("start_time")
        if st:
            try:
                dt = datetime.fromisoformat(st)
                ev["date_str"] = dt.date().isoformat()
                ev["time_str"] = dt.strftime("%H:%M")
            except Exception:
                ev["date_str"] = None
                ev["time_str"] = None
        return jsonify(ev)

    if request.method == "PUT":
        data = request.get_json() or {}
        ev["event"] = data.get("event", ev["event"])
        ev["start_time"] = fix_to_vn_tz(data.get("start_time", ev["start_time"]))
        ev["end_time"] = fix_to_vn_tz(data.get("end_time", ev["end_time"]))
        ev["location"] = data.get("location", ev["location"])
        ev["reminder_minutes"] = data.get("reminder_minutes", ev["reminder_minutes"])
        ev["color"] = data.get("color", ev.get("color") or "#22c55e")
        update_event(event_id, ev)
        return jsonify({"status":"ok"})

    if request.method == "DELETE":
        delete_event(event_id)
        return jsonify({"status":"ok"})

def fix_to_vn_tz(dt_str):
    if not dt_str:
        return None
    try:
        dt = datetime.fromisoformat(dt_str)
        if dt.tzinfo is None:
            # Datetime do frontend gửi phải được hiểu là giờ Việt Nam
            dt = dt.replace(tzinfo=TZ)
        else:
            dt = dt.astimezone(TZ)
        return dt.isoformat()
    except:
        return dt_str
    
@app.route("/api/search")
def api_search():
    q = request.args.get("q","")
    events = search_events(q) if q else []
    return jsonify({"events": events})

@app.route("/api/reminders")
def api_reminders():
    events = get_due_reminders()
    return jsonify({"events": events})

@app.route("/export/json")
def export_json():
    events = list_events()
    # Convert to JSON file download
    from flask import Response
    import json

    content = json.dumps(events, ensure_ascii=False, indent=2)
    return Response(
        content,
        mimetype="application/json",
        headers={"Content-Disposition": "attachment; filename=events_export.json"}
    )

@app.route("/export/ics")
def export_ics():
    events = list_events()

    def fmt(dt_str):
        """Convert ISO → ICS DATETIME e.g. 2025-12-01T13:20:00 → 20251201T132000"""
        if not dt_str:
            return ""
        try:
            dt = datetime.fromisoformat(dt_str)
            return dt.strftime("%Y%m%dT%H%M%S")
        except:
            return ""

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//VN NLP Calendar//EN"
    ]

    for ev in events:
        dt_start = fmt(ev["start_time"])
        dt_end = fmt(ev["end_time"]) if ev["end_time"] else ""

        lines.append("BEGIN:VEVENT")
        lines.append(f"UID:{ev['id']}@vncalendar")
        if dt_start:
            lines.append(f"DTSTART:{dt_start}")
        if dt_end:
            lines.append(f"DTEND:{dt_end}")
        lines.append(f"SUMMARY:{ev['event']}")
        if ev["location"]:
            lines.append(f"LOCATION:{ev['location']}")
        lines.append("END:VEVENT")

    lines.append("END:VCALENDAR")

    ics_content = "\r\n".join(lines)

    from flask import Response
    return Response(
        ics_content,
        mimetype="text/calendar",
        headers={"Content-Disposition": "attachment; filename=events_export.ics"}
    )

@app.route("/import/json", methods=["POST"])
def import_json():
    if "file" not in request.files:
        return jsonify({"status": "error", "message": "Thiếu file upload"}), 400

    file = request.files["file"]
    if not file.filename.endswith(".json"):
        return jsonify({"status":"error", "message": "File phải là .json"}), 400

    import json
    try:
        data = json.load(file)
    except Exception as e:
        return jsonify({"status":"error", "message": "File JSON không hợp lệ"}), 400

    if not isinstance(data, list):
        return jsonify({"status":"error", "message": "File JSON phải là list các events"}), 400

    imported = 0
    for ev in data:
        try:
            save_event_to_db({
                "event": ev.get("event"),
                "start_time": ev.get("start_time"),
                "end_time": ev.get("end_time"),
                "location": ev.get("location"),
                "reminder_minutes": ev.get("reminder_minutes", 0),
                "color": ev.get("color", "#22c55e"),
            })
            imported += 1
        except:
            continue

    return jsonify({"status": "ok", "imported": imported})

@app.get("/api/settings")
def api_get_settings():
    cfg = load_settings()
    return jsonify({
        "enable_sound": cfg.get("enable_sound", True),
        "sound_interval": cfg.get("sound_interval", 5),
        "notify_url": cfg.get("notify_url", "")
    })

@app.post("/api/settings")
def api_save_settings():
    data = request.json
    save_setting("enable_sound", json.dumps(data.get("enable_sound", True)))
    save_setting("sound_interval", json.dumps(data.get("sound_interval", 5)))
    save_setting("notify_url", json.dumps(data.get("notify_url", "")))
    return jsonify({"status": "ok"})


# ==============================
# MAIN
# ==============================

if __name__ == "__main__":
    # nên để debug=False để tránh tạo 2 thread reminder khi dùng reloader
    app.run(debug=False)
