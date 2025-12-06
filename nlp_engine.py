# nlp_engine.py

from utils.normalize import normalize_text, merge_time, normalize_relative_from_terms, normalize_specific_date
from nlp.preprocess import preprocess
from nlp.ner_extract import extract_ner
from nlp.rule_extract import extract_rule_based
from nlp.validator import build_event_dictionary
from datetime import datetime, timedelta
from utils.restore_tone_simple import restore_tone_simple
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Asia/Ho_Chi_Minh")

def process_text(text: str):
    # STEP 0 – ADD ACCENTS (Thêm dấu câu đơn giản nếu câu đó bị thiếu dấu)
    text = restore_tone_simple(text)
    print("ADD ACCENTS =", text)
    # STEP 1 – NORMALIZE FIRST STEP (chuẩn hóa câu để dễ xử lý)
    normalized = normalize_text(text)
    print("NORMALIZED FIRST STEP =", normalized)
    # STEP 2 – TOKENIZE
    tokens = preprocess(normalized)
    print("TOKENS =", tokens)
    # STEP 3 – NER (LOCATION)
    ner_data = extract_ner(normalized)
    print("LOCATION FROM NER =", ner_data)
    # STEP 4 – RULE-BASED EXTRACTION
    rule = extract_rule_based(tokens)
    print("RULE =", rule)
    # ---- DELAY TIME HANDLING ----
    now = datetime.now(TZ)
    delay_total = None
    
    if rule.get("delay_minutes"):
        delay_total = now + timedelta(minutes=rule["delay_minutes"])
    elif rule.get("delay_hours"):
        delay_total = now + timedelta(hours=rule["delay_hours"])
    elif rule.get("delay_days"):
        delay_total = now + timedelta(days=rule["delay_days"])

    if delay_total:
        # gán trực tiếp start_time
        start_dt = delay_total
        end_dt = None   # delay không có end time
        return {
            "event": rule["event"],
            "start_time": start_dt.isoformat(),
            "end_time": None,
            "location": rule.get("location"),
            "reminder_minutes": rule.get("reminder_minutes", 0)
        }

    event = rule["event"]
    time_raw_start = rule["time_raw"]
    time_raw_end = rule.get("time_raw_end")
    relative_terms = rule.get("relative_terms", [])
    specific_date_parts = rule.get("specific_date_parts")
    period_start = rule.get("period")
    period_end = rule.get("period_end") or period_start
    reminder = rule["reminder_minutes"]
    
    location_combined = []
    
    # Thêm toàn bộ LOCATION từ Model-based nếu có
    ner_locations = ner_data.get("locations")
    if ner_locations:
        if isinstance(ner_locations, list):
            location_combined.extend(ner_locations)
        elif isinstance(ner_locations, str):
            location_combined.append(ner_locations)

    # Thêm toàn bộ LOCATION từ Rule-based nếu có
    rule_location = rule.get("location")
    if rule_location:
        if isinstance(rule_location, list):
            location_combined.extend(rule_location)
        elif isinstance(rule_location, str):
            location_combined.append(rule_location)

    location = max(location_combined, key=len) if location_combined else None
    print("LOCATION FROM NER AND RULE = ", location_combined, " =>>> FINAL LOCATION =", location)

    # STEP 5 – TIME PARSING
    # Ưu tiên 1: Xử lý ngày tháng cụ thể (ngày 17 tháng 12)
    date_obj = normalize_specific_date(specific_date_parts)
    
    # Ưu tiên 2: Nếu không có ngày cụ thể, xử lý thời gian tương đối (ngày mai, tuần sau)
    if date_obj is None:
        date_obj = normalize_relative_from_terms(relative_terms)

    # Nếu vẫn không parse được → fallback hôm nay
    if date_obj is None:
        date_obj = datetime.now()
    
    print("TIME PARSING = ", date_obj)
    # Start datetime
    start_dt = merge_time(date_obj, time_raw_start, period_start)

    # End datetime (nếu có)
    end_dt = None
    if time_raw_end:
        end_dt = merge_time(date_obj, time_raw_end, period_end)
        # Nếu end <= start → hiểu là qua ngày mới
        if start_dt and end_dt and end_dt <= start_dt:
            end_dt = end_dt + timedelta(days=1)

    start_time = start_dt.isoformat() if start_dt else None
    end_time = end_dt.isoformat() if end_dt else None

    print("NORMALIZED RALATIVE TIME, MERGE TIME =", "START: ", start_time, "END: " ,end_time)

    # STEP 6 – FINAL OUTPUT
    output = build_event_dictionary(
        event=event,
        start_time=start_time,
        end_time=end_time,
        location=location,
        reminder=reminder,
    )

    return output
