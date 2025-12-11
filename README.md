# YouTube Downloader - Full-Stack Application

A full-stack YouTube video downloader with FastAPI backend and React frontend. Manage YouTube channels, download videos asynchronously with a task queue, monitor download progress in real-time, and browse complete download history.

## Configuration

Environment variables (backend/.env):

```bash
DATABASE_URL=sqlite:///./data/ytdownloader.db
HUEY_DB=./data/huey.db
DOWNLOAD_DIR=./downloads
API_PORT=8000
CORS_ORIGINS=http://localhost:5173,chrome-extension://*
DEBUG=false
YT_DLP_COOKIES_FILE=
```

### YouTube Authentication via Cookies

Some YouTube videos require an authenticated session. When yt-dlp logs:

```
Sign in to confirm you’re not a bot.
```

You can export cookies from your browser (see
[yt-dlp FAQ](https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp))
and point the backend at the resulting `cookies.txt` file via
`YT_DLP_COOKIES_FILE`. The backend will pass the file to yt-dlp when it
requests metadata, allowing it to access signed-in content.

Steps:

1. Export YouTube cookies using a browser extension or `yt-dlp --cookies-from-browser`.
2. Set `YT_DLP_COOKIES_FILE` in `backend/.env` to the exported file path.
3. Restart the backend API (and consumer, if running separately).
   │ │ ├── services/ # API client
   │ │ ├── types/ # TypeScript interfaces
   │ │ └── utils/ # Utility functions
   │ └── dist/ # Production build output
   │
   ├── data/ # SQLite databases
   └── downloads/ # Downloaded video files

````

## Technology Stack

### Backend
- **FastAPI** 0.124.0 - Modern Python web framework
- **SQLAlchemy** 2.0.44 - ORM with SQLite database
- **Huey** 2.5.5 - Task queue for background jobs
- **yt-dlp** 2025.12.8 - YouTube video downloader
- **Pydantic** 2.12.5 - Data validation

### Frontend
- **React** 19.2.0 - UI library
- **TypeScript** 5.9.3 - Type-safe JavaScript
- **Vite** 7.2.7 - Build tool and dev server
- **React Router** 7.10.1 - Client-side routing
- **Shadcn UI** - Component library with Tailwind CSS 4.1.17
- **Lucide React** 0.556.0 - Icon library

## Quick Start

See [specs/001-youtube-downloader/quickstart.md](specs/001-youtube-downloader/quickstart.md) for detailed setup and usage instructions.

### Prerequisites

- Python 3.10+
- Node.js 18+
- pnpm (or npm/yarn)

### Installation

1. **Clone repository**
   ```bash
   git clone <repository-url>
   cd yt-download-full-stack
````

2. **Backend setup**

   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Frontend setup**

   ```bash
   cd web
   pnpm install
   ```

4. **Create .env file**
   ```bash
   cp backend/.env.example backend/.env
   # Edit .env with your configuration
   ```

### Running the Application

**⚠️ IMPORTANT**: You need to run **3 processes** for the app to work:

1. **Backend API Server** (Terminal 1)

   ```bash
   cd backend
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   python main.py
   # Backend runs on http://localhost:8000
   ```

2. **Huey Task Consumer** (Terminal 2) - **REQUIRED for downloads to work!**

   ```bash
   cd backend
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   python run_consumer.py

   # Or using huey command directly:
   # python -m huey.consumer main.huey -v -w 2 -k thread
   ```

   ⚡ **Without this, downloads will queue but won't execute!**

   💡 **Alternative for Development**: Set `HUEY_IMMEDIATE_MODE=true` in `.env` to skip running consumer (tasks execute immediately)

3. **Frontend Dev Server** (Terminal 3)

   ```bash
   cd web
   pnpm dev
   # Frontend runs on http://localhost:5173
   ```

4. **Open browser**
   Navigate to http://localhost:5173

## Usage

### 1. Add Channels

- Go to "Channels" page
- Paste a YouTube channel URL
- Click "Add Channel"

### 2. Download Videos

- Go to "Downloads" page
- Paste one or more YouTube video URLs (one per line)
- Click "Download All"
- Videos are queued for download

### 3. Monitor Queue

- Go to "Queue" page
- View real-time download progress
- Retry failed downloads
- See pending, downloading, completed, and failed stats

### 4. Browse History

- Go to "History" page
- Search by video title
- Filter by date range or success/failure
- View statistics (total downloads, success rate, file size, etc.)

## API Documentation

Once running, visit http://localhost:8000/docs for interactive API documentation (Swagger UI).

### Key Endpoints

- `GET /api/channels` - List all channels
- `POST /api/channels` - Add new channel
- `POST /api/downloads/batch-urls` - Queue multiple downloads
- `GET /api/queue/status` - Get queue summary with active tasks
- `GET /api/history` - Get download history with filters
- `GET /api/history/stats` - Get download statistics

## Development

### Backend Testing

```bash
cd backend
pytest
```

### Frontend Type Checking

```bash
cd web
pnpm type-check
```

### Building for Production

```bash
# Backend - runs directly with Python
cd backend
python main.py

# Frontend - build static files
cd web
pnpm build
# Output in web/dist/
```

## Database Schema

- **Channel**: YouTube channels being tracked
- **DownloadTask**: Active/pending download jobs
- **DownloadHistory**: Complete record of all downloads

See [specs/001-youtube-downloader/data-model.md](specs/001-youtube-downloader/data-model.md) for detailed schema.

## Configuration

Environment variables (backend/.env):

```bash
DATABASE_URL=sqlite:///./data/ytdownloader.db
HUEY_DB=./data/huey.db
DOWNLOAD_DIR=./downloads
API_PORT=8000
CORS_ORIGINS=http://localhost:5173,chrome-extension://*
DEBUG=false
YT_DLP_COOKIES_FILE=
```

### YouTube Authentication via Cookies

Some YouTube videos require an authenticated session. When yt-dlp logs:

```
Sign in to confirm you’re not a bot.
```

You can export cookies from your browser (see
[yt-dlp FAQ](https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp))
and point the backend at the resulting `cookies.txt` file via
`YT_DLP_COOKIES_FILE`. The backend will pass the file to yt-dlp when it
requests metadata, allowing it to access signed-in content.

Steps:

1. Export YouTube cookies using a browser extension or `yt-dlp --cookies-from-browser`.
2. Set `YT_DLP_COOKIES_FILE` in `backend/.env` to the exported file path.
3. Restart the backend API (and consumer, if running separately).

## License

[Your License Here]

## Contributing

[Your Contribution Guidelines]

## Support

For issues and questions, please use the GitHub issue tracker.
