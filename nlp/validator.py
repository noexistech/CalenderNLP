# nlp/validator.py

def build_event_dictionary(event, start_time, end_time, location, reminder):
    """
    Module 5: Hợp nhất, kiểm tra lỗi, build output dictionary.
    - event: nội dung sự kiện (str hoặc None)
    - start_time: ISO datetime string hoặc None
    - end_time: ISO datetime string hoặc None
    - location: địa điểm (str, có thể rỗng)
    - reminder: số phút nhắc trước (int)
    """
    return {
        "event": event,
        "start_time": start_time,
        "end_time": end_time,
        "location": location,
        "reminder_minutes": reminder,
    }
