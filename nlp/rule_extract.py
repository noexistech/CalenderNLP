# nlp/rule_extract.py
import re
from utils.normalize import normalize_time

def extract_rule_based(tokens):
    text = " ".join(tokens)

    # =====================================
    # 1) START TIME (named group)
    # =====================================
    start_pattern = r"lúc\s+(?P<start_time>\d{1,2}\s*[:hgiờ]\s*\d{0,2})"
    start_match = re.search(start_pattern, text)
    time_raw_start = normalize_time(start_match.group("start_time")) if start_match else None

    # =====================================
    # 2) EVENT — chỉ lấy trước start_time đầu tiên
    # =====================================
    event = None
    if start_match:
        before = text[:start_match.start()]
        m = re.search(r"nhắc tôi (.+)", before)
        if not m:
            m = re.search(r"nhắc (.+)", before)
        event = m.group(1).strip() if m else None

    # =====================================
    # 3) LOCATION — pattern-based
    # =====================================
    loc_match = re.search(r"(?:ở|tại)\s+([a-z0-9_ ]+)", text)
    location = loc_match.group(1).strip() if loc_match else None

    # =====================================
    # 4) END TIME (multi-keywords, named groups)
    # =====================================
    end_pattern = (
        r"(?P<keyword>kết thúc(?: buổi| phiên)?|"
        r"hoàn thành|"
        r"chấm dứt|"
        r"bế mạc|"
        r"hết|"
        r"tan)"
        r"\s+lúc\s+"
        r"(?P<end_time>\d{1,2}\s*[:hgiờ]\s*\d{0,2})"
    )

    end_match = re.search(end_pattern, text)
    time_raw_end = normalize_time(end_match.group("end_time")) if end_match else None

    # =====================================
    # 5) RELATIVE TIME
    # =====================================
    relative_regex = (
        r"(sáng mai|chiều mai|tối mai|mai|ngày mai|"
        r"sáng nay|chiều nay|tối nay|hôm nay|nay|"
        r"sáng mốt|chiều mốt|tối mốt|mốt|"
        r"sáng ngày kia|chiều ngày kia|tối ngày kia|ngày kia|"
        r"hôm qua|hôm kia|hôm trước|"
        r"tuần sau nữa|tuần tới nữa|tuần sau|tuần tới|tuần này|"
        r"tuần trước nữa|tuần trước|tuần rồi|"
        r"thứ hai|thứ ba|thứ tư|thứ năm|thứ sáu|thứ bảy|chủ nhật)"
    )
    relative_terms = re.findall(relative_regex, text)
    relative = " ".join(relative_terms) if relative_terms else None

    # =====================================
    # 6) PERIOD
    # =====================================
    period_regex = r"(sáng|trưa|chiều|tối|đêm)"
    period_matches = list(re.finditer(period_regex, text))
    period_start = period_matches[0].group(1) if period_matches else None
    period_end   = period_matches[-1].group(1) if period_matches else period_start

    # =====================================
    # 7) REMINDER
    # =====================================
    reminder_match = re.search(r"nhắc trước (\d+) phút", text)
    reminder_minutes = int(reminder_match.group(1)) if reminder_match else 0

    return {
        "event": event,
        "location": location,
        "time_raw": time_raw_start,
        "time_raw_end": time_raw_end,
        "relative": relative,
        "relative_terms": relative_terms,
        "period": period_start,
        "period_end": period_end,
        "reminder_minutes": reminder_minutes,
    }
