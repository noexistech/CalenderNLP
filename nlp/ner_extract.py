# nlp/ner_extract.py
from underthesea import ner
import re

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


def extract_ner(text: str):
    entities = ner(text)
    locations = []

    # -------------------------------------------------
    # 1. LOCATION từ Underthesea nhưng phải lọc blacklist
    # -------------------------------------------------
    for token, pos, chunk, entity in entities:
        if entity == "B-LOC":
            t = token.lower().strip()

            # loại bỏ nhầm lẫn
            if t in BAD_LOCATIONS:
                continue

            # bỏ token 1 kí tự hoặc toàn số
            if t.isdigit():
                continue

            locations.append(token)

    # -------------------------------------------------
    # 2. RULE-BASED: phòng + số
    # -------------------------------------------------
    room = re.search(r"phòng\s+\d+", text.lower())
    if room:
        locations.append(room.group())

    # -------------------------------------------------
    # 3. RULE-BASED: sau từ “tại" hoặc "ở"
    # -------------------------------------------------
    at_match = re.search(r"(tại|ở)\s+([a-zA-ZÀ-ỹ0-9\s]+)", text.lower())
    if at_match:
        raw = at_match.group(2).strip()

        raw = raw.split(",")[0]

        if raw not in BAD_LOCATIONS:
            locations.append(raw)

    # -------------------------------------------------
    # 4. ƯU TIÊN RULE → loại trùng → giữ cái đúng
    # -------------------------------------------------
    unique_locations = list(dict.fromkeys(locations))

    return {"locations": unique_locations}
