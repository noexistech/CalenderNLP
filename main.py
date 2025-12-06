from nlp_engine import process_text

tests = [
    "Nhắc tôi chiều ngày kia đi tập thể dục ở công viên Hoàng Văn Thụ lúc 5h, nhắc trước 30 phút",
    "Nhắc tôi sáng ngày 2 tháng 1 năm 2026 đi họp lớp ở phòng c103 lúc 8h , nhắc trước 50 phút",
    "Nhắc tôi sáng mai dậy tập thể dục lúc 7 giờ 15 ở công viên Hoàng Văn Thụ",
    "Nhắc tôi Cafe sáng cn tuần sau nữa với nhóm bạn cấp 3 ở Highland coffee",
    "Nhắc tôi đi tắt bếp sau 15 phút, nhắc trước 1 phút.",
    "nhắc tôi tối nay nhậu tại quán ốc đào lúc 11h , nhắc trước 60 phút.",
    "nhắc tôi tối nay lúc 11h nhậu tại quán ốc đào, nhắc trước 60 phút.",
    "Nhắc tôi họp lớp lúc 9 giờ ở phòng 302"
]

for i, text in enumerate(tests, start=1):
    print(f"\n===== TEST {i} =====")
    print("INPUT :", text)
    print("OUTPUT:", process_text(text))
