# nlp_engine.py

from utils.normalize import normalize_text, normalize_relative_time, merge_time, normalize_relative_from_terms
from nlp.preprocess import preprocess
from nlp.ner_extract import extract_ner
from nlp.rule_extract import extract_rule_based
from nlp.validator import build_event_dictionary
from datetime import datetime, timedelta
from utils.restore_tone_simple import restore_tone_simple

def process_text(text: str):
    """
    Pipeline NLP 5 bước theo đúng yêu cầu thầy:
    1. Normalize (chuẩn hóa tiếng Việt)
    2. Preprocess (tokenize)
    3. NER: nhận LOCATION
    4. Rule-based: event, time_raw, relative, reminder
    5. Parse time & Validate final dictionary
    """
    # ----------------------------------------------------------------------
    # STEP 0 – ADD ACCENTS (Thêm dấu câu đơn giản nếu câu đó bị thiếu dấu)
    # ----------------------------------------------------------------------
    text = restore_tone_simple(text)
    print("ADD ACCENTS =", text)
    # ----------------------------------------------------------------------
    # STEP 1 – NORMALIZE (chuẩn hóa câu để dễ xử lý)
    # ----------------------------------------------------------------------
    normalized = normalize_text(text)
    print("NORMALIZED =", normalized)
    # ----------------------------------------------------------------------
    # STEP 2 – TOKENIZE
    # ----------------------------------------------------------------------
    tokens = preprocess(normalized)
    print("TOKENS =", tokens)
    # ----------------------------------------------------------------------
    # STEP 3 – NER (LOCATION)
    # ----------------------------------------------------------------------
    ner_data = extract_ner(normalized)
    print("ner_data =", ner_data)
    location = max(ner_data["locations"], key=len) if ner_data["locations"] else None #Lấy chữ dài nhất
    print("LOCATION =", location)
    # ----------------------------------------------------------------------
    # STEP 4 – RULE-BASED EXTRACTION
    # ----------------------------------------------------------------------
    rule = extract_rule_based(tokens)
    print("RULE =", rule)

    event = rule["event"]
    time_raw_start = rule["time_raw"]
    time_raw_end = rule.get("time_raw_end")
    relative_terms = rule.get("relative_terms", [])
    period_start = rule.get("period")
    period_end = rule.get("period_end") or period_start
    reminder = rule["reminder_minutes"]

    # STEP 5 – TIME PARSING
    # Dùng mảng relative_terms thay vì 1 string
    date_obj = normalize_relative_from_terms(relative_terms)

    # Nếu vẫn không parse được → fallback hôm nay
    if date_obj is None:
        date_obj = datetime.now()

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

    # STEP 6 – FINAL OUTPUT
    output = build_event_dictionary(
        event=event,
        start_time=start_time,
        end_time=end_time,
        location=location,
        reminder=reminder,
    )

    return output
