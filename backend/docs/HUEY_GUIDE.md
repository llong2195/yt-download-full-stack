# Huey Task Queue - Hướng Dẫn Sử Dụng

## Tự Động Tạo Database

✅ **Huey database được tự động tạo khi ứng dụng khởi động!**

- Database file: `data/huey.db`
- Tự động kiểm tra và tạo nếu chưa tồn tại
- Kiểm tra permissions và khả năng ghi
- Log confirmation khi database ready

**Xác minh setup:**
```bash
python verify_setup.py
```

---

## Vấn Đề: Tasks vào queue nhưng không chạy

**Nguyên nhân**: Huey cần một consumer process riêng để xử lý các task trong queue.

## Giải Pháp

### 1. Development Mode - Immediate Execution (Đơn giản nhất)

Tasks sẽ chạy ngay lập tức mà không cần consumer riêng.

**Cách bật:**
```bash
# Trong file .env, thêm:
HUEY_IMMEDIATE_MODE=true
```

**Khởi động lại backend:**
```bash
cd backend
python main.py
```

✅ **Ưu điểm**: Đơn giản, không cần process riêng  
❌ **Nhược điểm**: Không phù hợp production, blocking API nếu task chạy lâu

---

### 2. Production Mode - Consumer Process (Khuyến nghị)

Chạy Huey consumer trong terminal riêng để xử lý task background.

**Bước 1: Đảm bảo HUEY_IMMEDIATE_MODE=false trong .env**
```bash
HUEY_IMMEDIATE_MODE=false
```

**Bước 2: Chạy backend API**
```bash
cd backend
python main.py
```

**Bước 3: Trong terminal riêng, chạy Huey consumer**
```bash
cd backend
bash run_huey_consumer.sh

# Hoặc trực tiếp:
python -m huey.consumer main.huey -v -w 2 -k thread
```

✅ **Ưu điểm**: Phù hợp production, non-blocking, có thể scale  
✅ **Task chạy background thực sự**  
❌ **Nhược điểm**: Cần 2 terminal/process

---

## Kiểm Tra Task Queue

### Xem số task đang pending:
```bash
cd backend
python -c "from src.tasks.huey_instance import huey; print(f'Pending: {len(huey)}')"
```

### Xem log của consumer:
Consumer sẽ hiển thị log khi xử lý task:
```
[huey] 2025-12-09 10:30:00 - Executing download_video(task_id=1)
[huey] 2025-12-09 10:30:15 - download_video(task_id=1) succeeded
```

### Debug task execution:
```bash
cd backend
python -m huey.consumer main.huey -v -w 1 -k thread

# Options:
# -v: verbose mode (hiển thị chi tiết)
# -w 1: 1 worker (dễ debug)
# -k thread: thread-based worker
```

---

## Xử Lý Tasks Pending

Nếu có tasks pending mà consumer không chạy:

```bash
# 1. Kiểm tra số task
cd backend
python -c "from src.tasks.huey_instance import huey; print(f'Tasks: {len(huey)}')"

# 2. Chạy consumer với verbose mode
python -m huey.consumer main.huey -v -w 2 -k thread

# 3. Theo dõi log để xem task có execute không
```

---

## Cấu Hình Huey Consumer

### File: `run_huey_consumer.sh`

```bash
python -m huey.consumer main.huey -v -w 2 -k thread
```

**Tham số:**
- `-v`: Verbose logging
- `-w N`: Số worker threads (default: 1)
- `-k thread`: Worker type (thread/process/greenlet)
- `-d`: Delay between polling (ms)
- `-m N`: Số task tối đa một worker có thể chạy

### Ví dụ cấu hình khác:

```bash
# High throughput (nhiều download đồng thời)
python -m huey.consumer main.huey -w 5 -k thread

# Debug mode (chạy từng task)
python -m huey.consumer main.huey -v -w 1

# Production (background, no output)
python -m huey.consumer main.huey -w 4 -k thread > logs/huey.log 2>&1 &
```

---

## Testing

### Test task execution:
```bash
# Terminal 1: Start API
cd backend
python main.py

# Terminal 2: Start Huey consumer
cd backend
python -m huey.consumer main.huey -v -w 2 -k thread

# Terminal 3: Test download
curl -X POST http://localhost:8000/api/downloads/batch-urls \
  -H "Content-Type: application/json" \
  -d '{"video_urls": ["https://www.youtube.com/watch?v=dQw4w9WgXcQ"]}'
```

Bạn sẽ thấy log trong Terminal 2 khi task execute!

---

## Khuyến Nghị

- **Development**: Dùng `HUEY_IMMEDIATE_MODE=true` để test nhanh
- **Production**: Dùng consumer riêng với `HUEY_IMMEDIATE_MODE=false`
- **Monitoring**: Luôn chạy consumer với `-v` flag để theo dõi
- **Performance**: Tăng `-w` (workers) nếu cần xử lý nhiều downloads đồng thời

---

## Troubleshooting

### Task không chạy?
1. ✅ Kiểm tra consumer có đang chạy không
2. ✅ Kiểm tra HUEY_IMMEDIATE_MODE setting
3. ✅ Xem log consumer có báo lỗi không
4. ✅ Kiểm tra task có trong queue không: `len(huey)`

### Consumer crash?
1. Kiểm tra log lỗi
2. Thử chạy với 1 worker: `-w 1`
3. Kiểm tra database connection
4. Kiểm tra disk space

### Download không hoàn thành?
1. Kiểm tra yt-dlp có cài đặt không: `yt-dlp --version`
2. Kiểm tra network connection
3. Xem log chi tiết trong consumer output
4. Kiểm tra download_tasks table trong database
