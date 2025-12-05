# utils/datetime_helper.py

from datetime import datetime
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Asia/Ho_Chi_Minh")


def to_local(dt: datetime) -> datetime:
    """Đảm bảo datetime là timezone-aware (GMT+7)."""
    if dt is None:
        return None

    if dt.tzinfo is None:
        return dt.replace(tzinfo=TZ)

    return dt.astimezone(TZ)


def parse_iso(val: str) -> datetime:
    """Parse ISO 8601 (với hoặc không có timezone) thành aware datetime (GMT+7)."""
    if not val:
        return None

    try:
        dt = datetime.fromisoformat(val)
    except:
        return None

    return to_local(dt)


def parse_user_datetime(val: str) -> datetime:
    """
    Parse chuỗi user nhập:
    - "2025-12-05 11:06"
    - "2025-12-05T11:06"
    -> thành datetime aware GMT+7
    """
    if not val:
        return None

    try:
        if "T" in val:
            dt = datetime.fromisoformat(val)
        else:
            dt = datetime.strptime(val, "%Y-%m-%d %H:%M")
    except:
        return None

    return to_local(dt)


def iso(dt: datetime) -> str:
    """Convert datetime → ISO string có timezone."""
    if dt is None:
        return None
    return to_local(dt).isoformat()
