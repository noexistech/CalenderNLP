# utils/restore_tone_simple.py

DIACRITIC_MAP = {
    "nhac": "nhắc",
    "hop": "họp",
    "lop": "lớp",
    "gio": "giờ",
    "phong": "phòng",
    "sang": "sáng",
    "truoc": "trước",
    "phut": "phút",
    "mai": "mai",
}


def restore_tone_simple(text: str):
    words = text.lower().split()
    restored = []

    for i, w in enumerate(words):

        # CASE 1: toi = tối  (khi đứng trước từ chỉ thời gian)
        if w == "toi":
            if i + 1 < len(words) and words[i + 1] in ["mai", "nay", "qua", "sang", "chieu"]:
                restored.append("tối")
                continue

            # CASE 2: toi = tôi  (đứng sau động từ)
            if i > 0 and words[i - 1] in ["nhac", "bao", "goi", "giup", "nhan", "nhan", "nhac", "de"]:
                restored.append("tôi")
                continue

            # DEFAULT
            restored.append("tôi")
            continue

        # CASE 3: các từ khác trong từ điển
        restored.append(DIACRITIC_MAP.get(w, w))

    return " ".join(restored)
