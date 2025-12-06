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
    # 1. LOCATION từ Underthesea / B-LOC and I-LOC
    # -------------------------------------------------
    for token, pos, chunk, entity in entities:
        if entity == "B-LOC" or entity == "I-LOC":
            t = token.lower().strip()

            # loại bỏ nhầm lẫn
            if t in BAD_LOCATIONS:
                continue

            # bỏ token 1 kí tự hoặc toàn số
            if t.isdigit():
                continue

            locations.append(token)

    unique_locations = list(dict.fromkeys(locations))
      
    return {"locations": unique_locations}
