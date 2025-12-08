# Quick Start - Database Setup

## ✅ Tự Động Khởi Tạo

Backend tự động kiểm tra và tạo **tất cả** database cần thiết khi khởi động:

1. **Main Database** (`data/ytdownloader.db`) - Channels, Tasks, History
2. **Huey Database** (`data/huey.db`) - Task Queue
3. **Directories** - `data/`, `downloads/`

## 🚀 Lần Đầu Sử Dụng

### Option 1: Khởi tạo thủ công (khuyến nghị)
```bash
cd backend
python init_db.py
```

### Option 2: Tự động khi chạy app
```bash
cd backend
python main.py
# Databases sẽ được tạo tự động nếu chưa tồn tại
```

## 🔍 Kiểm Tra Setup

### Verify toàn bộ setup:
```bash
cd backend
python verify_setup.py
```

Kết quả mong đợi:
```
✅ ALL DATABASE CHECKS PASSED

📝 SUMMARY:
   • Main database:  ✅ Ready
   • Huey database:  ✅ Ready
   • Directories:    ✅ Created
   • Configuration:  ✅ Loaded
```

### Kiểm tra nhanh Huey:
```bash
cd backend
python test_huey.py
```

## 📁 Cấu Trúc Database

```
backend/
├── data/
│   ├── ytdownloader.db    # Main application database
│   │                      # Tables: channels, download_tasks, download_history
│   │                      # Auto-created on startup
│   │
│   └── huey.db           # Task queue database
│                         # Stores pending/executing tasks
│                         # Auto-created on startup
│
└── downloads/            # Video storage (organized by channel_id)
```

## ⚙️ Configuration (.env)

```bash
# Main database
DATABASE_URL=sqlite:///./data/ytdownloader.db

# Huey task queue
HUEY_DB=./data/huey.db
HUEY_IMMEDIATE_MODE=true  # true: tasks run immediately (dev)
                          # false: need consumer (production)

# Downloads
DOWNLOAD_DIR=./downloads
```

## 🔧 Troubleshooting

### Database không tạo được?
```bash
# Kiểm tra permissions
ls -la data/

# Tạo thủ công
mkdir -p data downloads
python init_db.py
```

### Huey database corrupt?
```bash
# Xóa và tái tạo
rm -f data/huey.db
python verify_setup.py
```

### Verify database tables:
```bash
sqlite3 data/ytdownloader.db ".tables"
# Expected: channels  download_history  download_tasks
```

## 🎯 Best Practices

1. **Development**: Use `HUEY_IMMEDIATE_MODE=true`
   - No consumer needed
   - Tasks execute instantly
   - Easy debugging

2. **Production**: Use `HUEY_IMMEDIATE_MODE=false`
   - Run consumer separately: `python run_consumer.py`
   - Better performance
   - Scalable

3. **Backup**: Regular backups of `data/` folder
   ```bash
   tar -czf backup-$(date +%Y%m%d).tar.gz data/
   ```

4. **Clean Start**: Reset all data
   ```bash
   rm -rf data/ downloads/
   python init_db.py
   ```

## 📊 Monitoring

### Check database sizes:
```bash
du -sh data/*.db
# ytdownloader.db: ~100KB-10MB (depends on usage)
# huey.db: ~0-1MB (grows with pending tasks)
```

### Check pending tasks:
```bash
python -c "from src.tasks.huey_instance import huey; print(f'Pending: {len(huey)}')"
```

### SQLite CLI:
```bash
# Main database
sqlite3 data/ytdownloader.db

# Useful queries:
.schema channels
.schema download_tasks
SELECT COUNT(*) FROM download_history;
SELECT status, COUNT(*) FROM download_tasks GROUP BY status;
```

## ✅ Success Indicators

When everything is set up correctly, you'll see:

```bash
# On startup (main.py):
2025-12-09 02:49:42 | INFO | Huey database ready: ./data/huey.db
2025-12-09 02:49:42 | INFO | ✅ Huey database verified
✓ FFmpeg ready

# On verify:
✅ ALL DATABASE CHECKS PASSED

# On test:
✅ IMMEDIATE MODE ENABLED
Tasks will execute immediately (no consumer needed)
```

---

**🎉 If you see these messages, your setup is perfect!**
