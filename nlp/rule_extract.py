# nlp/rule_extract.py
import re
from utils.normalize import normalize_time

BAD_LOCATIONS = [
    "nhóm", "nhom",
    "tuần",
    "lớp", "lop",
    "đội", "doi",
    "ban",
    "tổ", "to",
    "họp", "hop",
    "làm", "lam",
    "gặp", "gap",
    "lúc", "luc",
    "09", "9", "10", "11",
]

def extract_rule_based(tokens):
    text = " ".join(tokens)

    # =====================================
    # 0) SPECIFIC DATE (ngày dd tháng mm năm yyyy)
    # =====================================
    # Pattern để bắt các định dạng ngày tháng khác nhau
    # Thêm điều kiện để tránh bắt nhầm số trong "thứ 7".
    # Một số được coi là ngày NẾU:
    # 1. Có "ngày" đứng trước (ngày 17)
    # 2. Có "tháng" đứng sau (17 tháng 12)
    date_pattern = r"(?:(?P<prefix>ngày)\s+)?(?P<day>\d{1,2})(?:\s*tháng\s+(?P<month>\d{1,2}))(?:\s*năm\s+(?P<year>\d{4}))?|(?P<prefix2>ngày)\s+(?P<day2>\d{1,2})"
    date_match = re.search(date_pattern, text)
    specific_date_parts = date_match.groupdict() if date_match else None


    # =====================================
    # 1) START TIME (named group)
    # =====================================
    start_pattern = r"lúc\s+(?P<start_time>\d{1,2}\s*[:hgiờ]\s*\d{0,2})"
    start_match = re.search(start_pattern, text)
    time_raw_start = normalize_time(start_match.group("start_time")) if start_match else None

    # =====================================
    # 2) EVENT — chỉ lấy trước start_time đầu tiên
    # =====================================
    # = None
    #if start_match:
    #    before = text[:start_match.start()]
    #    m = re.search(r"nhắc tôi (.+)", before)
    #    if not m:
    #       m = re.search(r"nhắc (.+)", before)
    #    event = m.group(1).strip() if m else None

    # =====================================
    # 3) LOCATION — pattern-based
    #     Ví dụ: "ở phòng 302, nhắc trước 5 phút"
    #     -> location = "phòng 302"
    # =====================================
    loc_match = re.search(r"(?:ở|tại)\s+([^,\.]+)", text)
    
    locations = []

    # Cho phép phòng có tên bằng chữ hoặc số (phòng 101, phòng A)
    # \w+ sẽ khớp với chữ, số và dấu gạch dưới
    room = re.search(r"phòng\s+\w+", text.lower())
    if room:
        locations.append(room.group())

    # Cải tiến: Dừng lại khi gặp các từ khóa thời gian (lúc, vào, ngày, thứ,...)
    at_match = re.search(r"(tại|ở)\s+([^,]+?)(?=\s+(?:lúc|vào|ngày|thứ)|$)", text.lower())
    if at_match:
        raw = at_match.group(2).strip()

        # Không cần split(",") nữa vì regex đã xử lý
        if raw not in BAD_LOCATIONS:
            locations.append(raw)

    unique_locations = list(dict.fromkeys(locations))

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
    #    - Bổ sung dạng số: "thứ 2,3,4,5,6,7"
    #    - Sau đó chuẩn hóa:
    #        "thứ 2" -> "thứ hai", ...
    #        "thứ 7" -> "thứ bảy"
    # =====================================
    relative_regex = (
        r"(sáng mai|chiều mai|tối mai|mai|ngày mai|"
        r"sáng nay|chiều nay|tối nay|hôm nay|nay|"
        r"sáng mốt|chiều mốt|tối mốt|mốt|"
        r"sáng ngày kia|chiều ngày kia|tối ngày kia|ngày kia|"
        r"hôm qua|hôm kia|hôm trước|"
        r"tuần sau nữa|tuần tới nữa|tuần sau|tuần tới|tuần này|"
        r"tuần trước nữa|tuần trước|tuần rồi|"
        r"thứ hai|thứ ba|thứ tư|thứ năm|thứ sáu|thứ bảy|chủ nhật|"
        r"thứ 2|thứ 3|thứ 4|thứ 5|thứ 6|thứ 7)"
    )
    relative_terms = re.findall(relative_regex, text)

    # Chuẩn hóa "thứ 2,3,4,5,6,7" -> "thứ hai, ba, tư, năm, sáu, bảy"
    weekday_map = {
        "thứ 2": "thứ hai",
        "thứ 3": "thứ ba",
        "thứ 4": "thứ tư",
        "thứ 5": "thứ năm",
        "thứ 6": "thứ sáu",
        "thứ 7": "thứ bảy",
    }
    if relative_terms:
        normalized_terms = [weekday_map.get(t, t) for t in relative_terms]
        relative_terms = normalized_terms
        relative = " ".join(relative_terms)
    else:
        relative = None

    # =====================================
    # 6) PERIOD
    # =====================================
    period_regex = r"(sáng|trưa|chiều|tối|đêm)"
    period_matches = list(re.finditer(period_regex, text))
    period_start = period_matches[0].group(1) if period_matches else None
    period_end = period_matches[-1].group(1) if period_matches else period_start

    # =====================================
    # 7) REMINDER
    # =====================================
    reminder_match = re.search(r"nhắc trước (\d+) phút", text)
    reminder_minutes = int(reminder_match.group(1)) if reminder_match else 0

    # =====================================
    # 2) EVENT (- Loại bỏ hết và sự kiện còn lại cuối cùng)
    # =====================================
    event_text = text

    # Xóa từ nhắc tôi lúc bắt đầu
    event_text = re.sub(r"nhắc(?: tôi)?\s*", "", event_text, count=1)

    # Bỏ thgian, thứ ngày, lời nhắc, địa điểm trong câu gốc
    # Cập nhật: Xóa cả chuỗi thời gian đã tìm thấy bằng logic mới
    if time_raw_start: event_text = event_text.replace(time_raw_start, "")
    if start_match: event_text = event_text.replace(start_match.group(0), "")
    if date_match: event_text = event_text.replace(date_match.group(0), "")
    if loc_match: event_text = event_text.replace(loc_match.group(0), "")
    if end_match: event_text = event_text.replace(end_match.group(0), "")
    if reminder_match: event_text = event_text.replace(reminder_match.group(0), "")

    # Bỏ mấy từ tương đối (tuần sau ... )
    for term in relative_terms: event_text = event_text.replace(term, "")
    if period_start: event_text = event_text.replace(period_start, "")
    if period_end: event_text = event_text.replace(period_end, "")

    # Dọn dẹp cuối cùng: xóa các dấu câu thừa và khoảng trắng
    event_text = re.sub(r"[,.]", "", event_text)
    event = re.sub(r"\s+", " ", event_text).strip()

    return {
        "event": event,
        "location": unique_locations,
        "time_raw": time_raw_start,
        "time_raw_end": time_raw_end,
        "relative": relative,
        "specific_date_parts": specific_date_parts,
        "relative_terms": relative_terms,
        "period": period_start,
        "period_end": period_end,
        "reminder_minutes": reminder_minutes,
    }
