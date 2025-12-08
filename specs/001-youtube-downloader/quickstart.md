# Quickstart Guide: YouTube Downloader Full-Stack Application

**Feature**: [001-youtube-downloader](spec.md)  
**Date**: 2025-12-08  
**Purpose**: Step-by-step guide to set up and run the application

---

## Prerequisites

### Required Software

- **Python**: 3.10 or higher
- **Node.js**: 18.x or higher
- **pnpm**: Latest version (`npm install -g pnpm`)
- **yt-dlp**: Latest version
- **Git**: For version control

### Installation Commands

```bash
# Check versions
python --version  # Should be >= 3.10
node --version    # Should be >= 18.x
pnpm --version    # Should be >= 8.x

# Install yt-dlp
pip install yt-dlp

# Or on Windows with pipx
pipx install yt-dlp

# Verify yt-dlp
yt-dlp --version
```

---

## Quick Setup (5 minutes)

### 1. Clone Repository

```bash
git clone <repository-url>
cd yt-download-full-stack
```

### 2. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create data and downloads directories
mkdir -p ../data ../downloads

# Initialize database
python -c "from models.database import Base, engine; Base.metadata.create_all(engine)"

# Run backend
python main.py
```

Backend should now be running on `http://localhost:8000`

### 3. Frontend Setup (New Terminal)

```bash
# Navigate to frontend
cd web

# Install dependencies
pnpm install

# Start development server
pnpm dev
```

Frontend should now be running on `http://localhost:5173`

### 4. Verify Setup

Open browser: `http://localhost:5173`

You should see:

- Empty channel list
- "Add Channel" button
- Navigation menu (Channels, Downloads, Queue, History)

---

## Detailed Setup

### Backend Configuration

#### requirements.txt

```txt
fastapi==0.124.0
uvicorn==0.38.0
SQLAlchemy==2.0.44
pydantic==2.12.5
huey==2.5.5
yt-dlp==2025.12.8
```

#### Environment Variables (Optional)

Create `backend/.env`:

```env
# Database
DATABASE_URL=sqlite:///data/app.db
HUEY_DB=data/huey.db

# Downloads
DOWNLOAD_DIR=downloads/

# API
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:5173,chrome-extension://*

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

#### main.py Structure

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from threading import Thread
from huey import SqliteHuey
import uvicorn

# Import routers
from routers import channels, downloads, queue, history

# Initialize Huey
huey = SqliteHuey(filename='data/huey.db')

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start Huey consumer
    consumer_thread = Thread(target=huey.start, daemon=True)
    consumer_thread.start()
    yield
    # Shutdown: Stop Huey
    huey.stop()

app = FastAPI(title="YouTube Downloader API", version="1.0.0", lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "chrome-extension://*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(channels.router, prefix="/api/channels", tags=["channels"])
app.include_router(downloads.router, prefix="/api/downloads", tags=["downloads"])
app.include_router(queue.router, prefix="/api/queue", tags=["queue"])
app.include_router(history.router, prefix="/api/history", tags=["history"])

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "version": "1.0.0"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Frontend Configuration

#### package.json (Key Dependencies)

```json
{
  "name": "yt-downloader-web",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "test": "vitest"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.43",
    "@types/react-dom": "^18.2.17",
    "@vitejs/plugin-react": "^4.2.1",
    "typescript": "^5.3.3",
    "vite": "^5.0.8",
    "vitest": "^1.0.4"
  }
}
```

#### vite.config.ts

```typescript
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
```

#### src/services/api.ts (Base Fetch Wrapper)

```typescript
const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export async function apiFetch<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.user_message || "API request failed");
  }

  return response.json();
}
```

---

## Running the Application

### Development Mode

**Terminal 1: Backend API Server**

```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2: Huey Task Consumer** (Required for downloads to execute)

```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
python -m huey.consumer main.huey
```

The Huey consumer processes background download tasks. Without it running:
- Videos can be queued via the Downloads page
- Tasks will be created in the database
- But actual downloads won't execute until the consumer starts

**Terminal 3: Frontend Dev Server**

```bash
cd web
pnpm dev
```

Access: `http://localhost:5173`

### Production Build

#### Backend (Production)

```bash
cd backend

# Install production dependencies
pip install -r requirements.txt

# Run with Gunicorn (Linux/macOS)
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Or with Uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

#### Frontend (Production)

```bash
cd web

# Build for production
pnpm build

# Output in dist/ folder
# Serve with any HTTP server:

# Option 1: Python HTTP server
cd dist
python -m http.server 8080

# Option 2: Serve (npm package)
npx serve -s dist -p 8080

# Option 3: Nginx (copy dist/ to /var/www/html)
# Option 4: Apache, Caddy, etc.
```

Access: `http://localhost:8080`

**Important**: Update `VITE_API_BASE` in frontend to production backend URL before building:

```bash
# Create .env.production in web/
VITE_API_BASE=https://api.yourdomain.com
```

---

## Testing the Application

### 1. Add a Channel (Optional - Auto-created during download)

1. Open `http://localhost:5173`
2. Navigate to "Channels" page
3. Enter YouTube channel URL: `https://www.youtube.com/@channelname`
4. Click "Add Channel"
5. Channel should appear in list

**Note**: Channels are automatically created when you download videos, so this step is optional.

### 2. Request Batch Downloads

1. Navigate to "Downloads" page (`http://localhost:5173/downloads`)
2. Paste YouTube video URLs (one per line) in the textarea, for example:
   ```
   https://www.youtube.com/watch?v=dQw4w9WgXcQ
   https://youtu.be/jNQXAC9IVRw
   https://www.youtube.com/watch?v=9bZkp7q19f0
   ```
3. Click "Download All"
4. See results:
   - Summary: X requested, Y queued, Z skipped
   - Task list with video IDs and status badges
   - Any errors or skipped videos

**Important**: Make sure the Huey consumer is running (Terminal 2) for downloads to actually execute!

### 3. Monitor Download Progress (Queue Page - Coming Soon)

**Note**: Queue monitoring page is not yet implemented. Current progress:
- Tasks are created and queued successfully
- Downloads execute in background via Huey
- Can verify downloads by checking database or file system

To check download status manually:
```bash
# Check database
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
python -c "from src.models.database import SessionLocal; from src.repository import download_repo; db = SessionLocal(); tasks = download_repo.get_all_active_tasks(db); print(f'Active tasks: {len(tasks)}'); [print(f'- {t.video_id}: {t.status} ({t.progress_percent}%)') for t in tasks]"
```

### 4. Check Downloaded Files

```bash
# List downloaded files
ls -lh downloads/

# Should see structure like:
# downloads/UC_channel_id/video_id.mp4
```

### 5. View Download History (Coming Soon)

**Note**: History page is not yet implemented. History records are being created in the database during downloads.

---

## API Testing (Manual)

### Using cURL

```bash
# Health check
curl http://localhost:8000/api/health

# Add channel
curl -X POST http://localhost:8000/api/channels \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/@example"}'

# Get channels
curl http://localhost:8000/api/channels

# Request download
curl -X POST http://localhost:8000/api/downloads \
  -H "Content-Type: application/json" \
  -d '{"video_id": "dQw4w9WgXcQ"}'

# Check queue
curl http://localhost:8000/api/queue/status
```

### Using FastAPI Docs

Open `http://localhost:8000/docs`

- Interactive API documentation
- Try out endpoints directly in browser
- See request/response schemas

---

## Troubleshooting

### Backend Issues

**Problem**: `ModuleNotFoundError: No module named 'fastapi'`
**Solution**: Activate virtual environment and install dependencies

```bash
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Problem**: `Database is locked`
**Solution**: Enable WAL mode (should be automatic in database.py)

```python
with engine.connect() as conn:
    conn.execute("PRAGMA journal_mode=WAL")
```

**Problem**: `yt-dlp: command not found`
**Solution**: Install yt-dlp

```bash
pip install yt-dlp
# Or: pipx install yt-dlp
```

**Problem**: Download fails with "Rate limit exceeded"
**Solution**: Wait 15 minutes, YouTube has rate limits. Retry will happen automatically.

### Frontend Issues

**Problem**: `Failed to fetch` in console
**Solution**: Check backend is running on `http://localhost:8000`

```bash
curl http://localhost:8000/api/health
```

**Problem**: CORS error
**Solution**: Ensure CORS middleware configured in `main.py`

```python
allow_origins=["http://localhost:5173"]
```

**Problem**: `pnpm: command not found`
**Solution**: Install pnpm

```bash
npm install -g pnpm
```

---

## Development Workflow

### Making Changes

1. **Backend changes**:

   - Edit files in `backend/`
   - FastAPI auto-reloads (if using `--reload` flag)
   - Test endpoint in `http://localhost:8000/docs`

2. **Frontend changes**:

   - Edit files in `web/src/`
   - Vite hot-reloads automatically
   - See changes instantly in browser

3. **Database changes**:
   - Modify models in `backend/models/`
   - Drop database: `rm data/app.db`
   - Recreate: `python -c "from models.database import Base, engine; Base.metadata.create_all(engine)"`
   - Future: Use Alembic for migrations

### Testing

```bash
# Backend tests (future)
cd backend
pytest

# Frontend tests
cd web
pnpm test
```

---

## Deployment Checklist

### Backend

- [ ] Set `DATABASE_URL` to production database path
- [ ] Set `DOWNLOAD_DIR` to production storage location
- [ ] Configure `CORS_ORIGINS` to production frontend URL
- [ ] Set up logging to file (not just console)
- [ ] Use production WSGI server (Gunicorn, uWSGI)
- [ ] Set up reverse proxy (Nginx, Caddy)
- [ ] Enable HTTPS (Let's Encrypt)
- [ ] Set up monitoring (disk space, task queue)

### Frontend

- [ ] Set `VITE_API_BASE` to production backend URL
- [ ] Run `pnpm build`
- [ ] Test `dist/` folder locally
- [ ] Deploy `dist/` to web server
- [ ] Configure HTTP server for SPA routing
- [ ] Enable HTTPS
- [ ] Set up CDN (optional)

---

## Next Steps

1. **Add First Channel**: Test basic functionality
2. **Download a Video**: Verify Huey queue working
3. **Check History**: Ensure persistence working
4. **Read Documentation**:
   - [spec.md](spec.md) - Feature specification
   - [plan.md](plan.md) - Implementation plan
   - [data-model.md](data-model.md) - Database schema
   - [contracts/api-spec.md](contracts/api-spec.md) - API reference

---

## Support

- **API Docs**: `http://localhost:8000/docs`
- **Constitution**: `.specify/memory/constitution.md`
- **GitHub Issues**: <repository-url>/issues

---

## License

[Specify License]
