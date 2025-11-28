# nlp/time_parse.py
from datetime import datetime, timedelta
from dateutil import parser

def apply_relative_day(relative_word: str):
    """Chuyển 'mai', 'sáng mai' thành ngày tương ứng."""
    today = datetime.now()

    if not relative_word:
        return today.date()

    if "mai" in relative_word:
        return today.date() + timedelta(days=1)

    if "nay" in relative_word:
        return today.date()

    return today.date()


def parse_time(time_raw: str, relative: str):
    """
    Module 4: Ghép time_raw + relative → datetime ISO string.
    """
    if not time_raw:
        return None

    date = apply_relative_day(relative)
    date_str = date.strftime("%Y-%m-%d")

    full_str = f"{date_str} {time_raw}"

    try:
        dt = parser.parse(full_str, dayfirst=False)
        return dt.isoformat()
    except:
        return None
