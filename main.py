from nlp_engine import process_text

tests = [
    "Nhắc tôi tuần sau đi học lúc 7h vào thứ 3 ở phòng 102, nhắc trước 60 phut",
    "Nhắc tôi về quê sáng mốt",
    "Nhắc tôi có suất phim chiếu 12h đêm nay, nhắn trước 30 phút",
    "Ca trực đêm lúc 2h sáng mai.",
    "Nhắc tôi nộp bài tập tối nay lúc 23h50 trên sgu moodle.",
    "Ở sân SGU, nhắc tôi đá bóng chiều thứ 7 tuần sau lúc 17h.",
    "Nhắc tôi Thứ 2 tuần sau đi làm lại.",
    "Nhac toi di da banh san Thong Nhat chieu thu 5 tuan sau.",
    "Nhắc tôi sau 30 phút nữa gọi cho mẹ.",
    "Nhắc tôi 7 giờ sáng ngày 31 tháng 12 năm 2025 thi ở phòng c205 tại Đại Học Sài Gòn",
    "Nhắc tôi Đi bảo hành xe chiều tối hôm nay.",
    "Nhắc tôi đi tập gym vào sáng mai",
]

for i, text in enumerate(tests, start=1):
    print(f"\n===== TEST {i} =====")
    print("INPUT :", text)
    output = process_text(text)
    print("OUTPUT:", output)
