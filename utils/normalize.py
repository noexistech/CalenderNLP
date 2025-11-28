# utils/normalize.py
import re
from datetime import datetime, timedelta
from underthesea import text_normalize

WEEKDAY_MAP = {
    "thứ hai": 0,
    "thứ ba": 1,
    "thứ tư": 2,
    "thứ năm": 3,
    "thứ sáu": 4,
    "thứ bảy": 5,
    "chủ nhật": 6,
}

def normalize_text(text: str):
    #Lower case toàn bộ text input
    t = text.lower()

    #Dùng underthesea để loại bỏ khoảng trắng, các trường hợp input nhưng sai dấu
    t = text_normalize(t)

    # Case: 10 giờ 30 → 10:30
    t = re.sub(r"(\d{1,2})\s*giờ\s*(\d{1,2})", r"\1:\2", t)

    # Case: 10h30 → 10:30
    t = re.sub(r"(\d{1,2})h(\d{1,2})", r"\1:\2", t)

    # Case: 10h 30 → 10:30
    t = re.sub(r"(\d{1,2})h\s*(\d{1,2})", r"\1:\2", t)

    # Case: 10 giờ → 10:00
    t = re.sub(r"(\d{1,2})\s*giờ", r"\1:00", t)

    # Case: 10h → 10:00
    t = re.sub(r"(\d{1,2})h", r"\1:00", t)

    # Case: 3 rưỡi → 3:30
    t = re.sub(r"(\d{1,2})\s*rưỡi", r"\1:30", t)

    # Case: 3 giờ rưỡi → 3:30
    t = re.sub(r"(\d{1,2})\s*giờ\s*rưỡi", r"\1:30", t)

    # Case: 3 giờ  rưỡi  (thừa khoảng trắng)
    t = re.sub(r"(\d{1,2})\s*giờ\s*rưỡi", r"\1:30", t)

    return t

def normalize_time(t):
    t = t.strip()

    # 10 giờ 30 → 10:30
    t = t.replace("giờ", "h")
    t = t.replace(" ", "")

    # 10h30 → 10:30
    if re.match(r"\d{1,2}h\d{1,2}", t):
        return t.replace("h", ":")

    # 10h → 10:00
    if re.match(r"\d{1,2}h$", t):
        return t.replace("h", ":00")

    # 10:30 → giữ nguyên
    if ":" in t:
        return t

    return None

def normalize_relative_from_terms(terms):
    """
    Nhận 1 list các cụm thời gian tương đối, ví dụ:
    ["thứ hai", "tuần tới nữa"] hoặc ["thứ_tư", "tuần sau"]
    → Ghép lại thành chuỗi rồi đưa vào normalize_relative_time.
    """
    if not terms:
        return datetime.now()

    combined = " ".join(terms)
    return normalize_relative_time(combined)

def normalize_relative_time(raw_text: str):
    """
    Chuẩn hóa các cụm thời gian tương đối thành datetime đúng ngày:
    - mai, mốt, ngày kia
    - sáng mai, chiều mai, tối mai
    - sáng mốt, chiều mốt, tối mốt
    - sáng ngày kia, chiều ngày kia
    - hôm qua, hôm kia, hôm trước
    """
    today = datetime.now()

    if raw_text is None:
        return today  # fallback: nếu không biết → hôm nay

    # THÊM: thay "_" thành " " để khớp WEEKDAY_MAP
    text = raw_text.lower().replace("_", " ").strip()

    # === Ngày mai ===
    # Lưu ý: phải kiểm tra 'ngày mai' TRƯỚC 'mai' để tránh match sai
    if "ngày mai" in text:
        return today + timedelta(days=1)
    if "mai" in text:
        return today + timedelta(days=1)

    # === Mốt ===
    if "sáng mốt" in text or "chiều mốt" in text or "tối mốt" in text:
        return today + timedelta(days=2)
    if "mốt" in text:
        return today + timedelta(days=2)

    # === Ngày kia ===
    if "sáng ngày kia" in text or "chiều ngày kia" in text or "tối ngày kia" in text:
        return today + timedelta(days=2)
    if "ngày kia" in text:
        return today + timedelta(days=2)

    # === Hôm nay ===
    if "hôm nay" in text:
        return today
    if text == "nay":
        return today

    # === Hôm qua ===
    if "hôm qua" in text:
        return today - timedelta(days=1)

    # === Hôm kia ===
    if "hôm kia" in text:
        return today - timedelta(days=2)

    # === Hôm trước ===
    # Người Việt thường dùng nghĩa = hôm qua (phổ biến nhất)
    if "hôm trước" in text:
        return today - timedelta(days=1)

    # === TUẦN OFFSET (tuần sau, tuần sau nữa, tuần trước, tuần trước nữa) ===
    week_offset = 0  # đơn vị: số tuần

    if "tuần sau nữa" in text or "tuần tới nữa" in text:
        week_offset = 2
    elif "tuần sau" in text or "tuần tới" in text:
        week_offset = 1
    elif "tuần trước nữa" in text:
        week_offset = -2
    elif "tuần trước" in text or "tuần rồi" in text:
        week_offset = -1
    elif "tuần này" in text:
        week_offset = 0

    # Nếu có thứ + tuần (ví dụ: "thứ hai tuần sau nữa")
    for key, weekday_index in WEEKDAY_MAP.items():
        if key in text:
            # Tính Monday của tuần hiện tại
            current_wd = today.weekday()  # 0=Mon
            this_monday = today - timedelta(days=current_wd)
            # Monday của tuần đích
            target_monday = this_monday + timedelta(weeks=week_offset)
            # Ngày = Monday + offset theo weekday_index
            return target_monday + timedelta(days=weekday_index)

    # === Thứ trong tuần (thứ hai → chủ nhật) ===
    for key, weekday_index in WEEKDAY_MAP.items():
        if key in text:
            current_wd = today.weekday()
            diff = weekday_index - current_wd
            if diff <= 0:
                diff += 7
            return today + timedelta(days=diff)

    return None


def convert_hour_with_period(hour: int, period: str):
    period = period.lower().strip()

    # ==== SÁNG ====
    if "sáng" in period:
        if hour == 12:
            return 12  # theo logic bạn đang dùng: 12 giờ sáng = 12:00
        return hour

    # ==== TRƯA ====
    if "trưa" in period:
        if hour == 12:
            return 12
        return hour + 12  # 1 giờ trưa = 13h, 2 giờ trưa = 14h

    # ==== CHIỀU ====
    if "chiều" in period:
        if hour == 12:
            return 12
        return hour + 12  # 1 giờ chiều = 13h

    # ==== TỐI / ĐÊM ====
    if "tối" in period or "đêm" in period:
        if hour == 12:
            return 0  # 12 giờ tối = 00:00
        # Giả sử bạn dùng 'tối' cho khung giờ khuya 1–5h
        if 1 <= hour <= 5:
            return hour   # 1 giờ tối = 01:00, 3 giờ tối = 03:00
        # Nếu sau này bạn có 7 giờ tối, 8 giờ tối... thì map sang 19–23h:
        return hour + 12  # 7 giờ tối = 19:00, 8 giờ tối = 20:00

    # Không có buổi → giữ nguyên
    return hour

def merge_time(date_obj, time_raw: str, period_word: str = None):
    if not date_obj or not time_raw:
        return None

    hour, minute = map(int, time_raw.split(":"))

    # Nếu giờ > 12 mà người dùng vẫn ghi sáng / trưa / chiều / tối → bỏ period
    # Vì 14 giờ chiều, 18 giờ sáng, 13 giờ trưa… đều không hợp lệ.
    if period_word and hour > 12:
        period_word = None

    # === SPECIAL CASE: 12 giờ sáng ===
    if period_word and "sáng" in period_word and hour == 12:
        return date_obj.replace(hour=12, minute=minute, second=0)

    # === SPECIAL CASE: 12 giờ tối ===
    if period_word and "tối" in period_word and hour == 12:
        return date_obj.replace(hour=0, minute=minute, second=0)

    # === NORMAL CASE USING PERIOD ===
    if period_word:
        hour = convert_hour_with_period(hour, period_word)

    return date_obj.replace(hour=hour, minute=minute, second=0)




