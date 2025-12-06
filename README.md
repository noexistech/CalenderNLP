# 🌟 Vietnamese NLP Smart Calendar  
### *AI-powered Vietnamese Natural Language Calendar with Real-time Reminders*  

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-Web%20Framework-lightgrey?logo=flask)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5-purple?logo=bootstrap)
![NLP](https://img.shields.io/badge/NLP-Vietnamese-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 📖 Mục lục
- [🎯 Giới thiệu](#-giới-thiệu)
- [✨ Demo UI](#-demo-ui)
- [🏗️ Kiến trúc dự án](#️-kiến-trúc-dự-án)
- [🚀 Cách chạy](#-cách-chạy)
- [🧠 NLP Pipeline](#-nlp-pipeline)
- [📦 Database](#-database)
- [🖥️ Giao diện Web](#️-giao-diện-web)
- [🔔 Reminder Worker](#-reminder-worker)
- [⚡ API Documentation](#-api-documentation)
- [📤 Import / Export](#-import--export)
- [🧩 Features](#-features)
- [📘 Kết luận](#-kết-luận)

---

## 🎯 Giới thiệu  
Vietnamese NLP Smart Calendar là hệ thống AI hiểu câu tiếng Việt tự nhiên để tự động tạo sự kiện, thời gian, địa điểm, nhắc nhở — kèm giao diện hiện đại và hệ thống nhắc nhở real-time thông qua dịch vụ NTFY.SH 
Ứng dụng sử dụng thư viện underthesea cơ bản, kết hợp với regex để tạo Rule-Based để bắt các sự kiện, thời gian, địa điểm, nhắc nhở từ câu nhập Tiếng Việt, kết hợp thêm dịch vụ NTFY.SH để có thể gửi thông báo đến điện thoại của người dùng mỗi khi thời gian nhắc nhở gần đến

---

## ✨ Demo UI  

<img width="1920" height="752" alt="image" src="https://github.com/user-attachments/assets/d5c2ad94-d6db-4b0b-9600-f3915bb3096b" />
<img width="826" height="304" alt="image" src="https://github.com/user-attachments/assets/40b03cfe-97a1-4d41-98f1-d2ea7b417e6d" />
<img width="532" height="346" alt="image" src="https://github.com/user-attachments/assets/8cfef0ce-84cd-4c37-a40b-6ab146eebe64" />
<img width="830" height="597" alt="image" src="https://github.com/user-attachments/assets/2d4b1142-b37b-47ce-8261-7df8fd8f82c2" />
<img width="534" height="380" alt="image" src="https://github.com/user-attachments/assets/a35c85bc-80dd-42bd-8fa2-5514ce34aab4" />
<img width="644" height="240" alt="image" src="https://github.com/user-attachments/assets/da41ce99-cd8e-4703-bcc8-bdd8e5ef8676" />
<img width="502" height="210" alt="image" src="https://github.com/user-attachments/assets/1a0fa757-a836-4354-9943-403be4631265" />

---

## 🚀 Cách chạy  

### 1. Cài dependencies  
```
pip install flask underthesea
```

### 2. Chạy server  
```
python main_ui_web.py
```

### 3. Mở trình duyệt  
```
http://127.0.0.1:8080
```

---

## 🏗️ Kiến trúc dự án
```
root/
│── main.py          # CLI đơn giản để test câu trong quá trình code
│── main_ui_web.py          # Flask UI + API + Reminder thread
│
├── nlp/
│   ├── preprocess.py        # Chuẩn hóa câu, chuẩn bị NLP
│   ├── rule_extract.py      # Luật trích xuất event/time/location
│   ├── ner_extract.py       # NER đơn giản để tìm location
│   ├── validator.py         # Hợp nhất dữ liệu, build output final
│   └── nlp_engine.py        # Quản lý pipeline NLP
│
├── utils/
│   ├── restore_tone_simple.py # Phục hồi dấu tiếng Việt
│   ├── normalize.py         # Chuẩn hóa thời gian (h, giờ, 15h20 → 15:20)
│
├── storage/
│   ├── database.py          # SQLite: events + settings
│
│── events.db            # File DB SQL Lite
│
└── README.md
```

---

## 🧠 NLP Pipeline  

### 1. Khôi phục dấu  
Sử dụng regex đơn giản để khôi phục dấu câu khi người dùng nhập không dấu.
Ngữ cảnh đơn giản là bởi phần mềm có phạm vi nhỏ, có thể sử dụng regex để tìm kiếm các từ thường dùng mà không cần đến mô hình transformer phức tạp

### 2. Tiền xử lý  
Chuẩn hóa spacing, lowercase, xử lý số liệu thời gian.

### 3. Normalizer  
Chuyển “15h20”, “3 giờ rưỡi”, “8h tối” → thời gian chuẩn ISO.

### 4. Rule Extraction  
Nhận dạng:
- Tên sự kiện  
- Thời gian bắt đầu  
- Thời gian kết thúc  
- Địa điểm  
- Các từ khóa: “tuần sau”, “mai”, “thứ bảy”, “sáng”, “chiều”…  
- Nhắc trước N phút  

### 5. NER  
Trích xuất location từ câu.

### 6. Validator → Output Final  
Kết hợp rule-based + NER → chuẩn hóa thành:
```
{
  "event": "họp lớp",
  "start_time": "2025-12-05T13:20:00",
  "end_time": null,
  "location": "phòng 302",
  "reminder_minutes": 5
}
```

---

## 📦 Database  

### Bảng `events`
| id | event | start_time | end_time | location | reminder_minutes | color |
|----|--------|------------|----------|----------|------------------|--------|

### Bảng `settings`
| enable_sound | sound_interval | notify_url |
|--------------|----------------|------------|

---

## 🖥️ Giao diện Web  
✔ Modern UI bằng Bootstrap 5  
✔ Xem lịch tháng / tuần / ngày  
✔ Popup chi tiết sự kiện  
✔ Form chỉnh sửa với time picker  
✔ Tự động highlight ngày hiện tại  
✔ Sidebar thống kê  
✔ Import JSON  
✔ Export JSON / ICS  

---

## 🔔 Reminder Worker  

Chạy trong Thread riêng:

- Quét DB mỗi 10 giây  
- Tính giờ nhắc theo múi giờ GMT+7  
- Push notification → ntfy.sh  
- Phát âm thanh (optional)  
- Lặp lại tiếng theo interval user config  

---

## ⚡ API Documentation  

### `GET /api/events?year=&month=`
Lấy sự kiện trong tháng + thống kê.

### `POST /api/events`
Tạo sự kiện từ câu tiếng Việt:
```
{
  "natural_text": "Nhắc tôi họp lớp lúc 13h20 tuần sau..."
}
```

### `PUT /api/events/<id>`
Cập nhật sự kiện.

### `DELETE /api/events/<id>`
Xóa sự kiện.

### `GET /api/search?q=`
Tìm kiếm.

### `GET /api/reminders`
Trả về sự kiện đến giờ nhắc.

### `GET/POST /api/settings`
Lưu cài đặt.

---

## 📤 Import / Export  

### Import JSON
Tải file `events.json` để nhập toàn bộ sự kiện.

### Export JSON
Xuất tất cả sự kiện để backup.

### Export ICS  
Tạo file chuẩn `.ics` tương thích Google Calendar / Outlook.

---

## 🧩 Features  

- 🎯 Hiểu ngôn ngữ tự nhiên tiếng Việt cơ bản
- 🕒 Có thể nhận thời gian tương đối (15h20 sáng tuần sau thứ bảy…)  
- 📍 Có thể nhận diện địa điểm cơ bản qua NER
- 🔔 Nhắc nhở real-time
- 📱 Push notification đến điện thoại (ntfy.sh)
- 🎨 Event color tagging  
- 💾 Import / Export JSON + ICS  
- 🔍 Tìm kiếm sự kiện  
- 📊 Thống kê đơn giản theo tháng / tuần

---

## 📘 Kết luận  

Dự án xây dựng một **trợ lý lịch thông minh cho người Việt**, linh hoạt, tiện dụng, có thể mở rộng để tích hợp các mô hình để bắt chính xác hơn, mạnh hơn trong tương lai.

---

*Made with ❤️ for Vietnamese users.*
