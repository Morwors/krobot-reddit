# Reddit Video Generator

A full-stack application for generating Reddit-style short-form videos (TikTok, YouTube Shorts, Reels) with AI-powered text-to-speech narration and karaoke-style subtitles.

## Features

- **Reddit Scraping**: Scrape posts from any Reddit URL (AITA, AskReddit, etc.) — no API key needed
- **Manual Input**: Paste your own script for custom content
- **Local TTS**: Deep male narrator voice using Coqui TTS (fully local, no API calls)
- **Karaoke Subtitles**: Word-by-word highlighted subtitles using faster-whisper
- **Video Assembly**: Professional 9:16 vertical video output via FFmpeg
- **Job Queue**: Async video generation with Celery + Redis
- **Modern UI**: Dark-themed React frontend with shadcn/ui components

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Frontend   │────▶│   Backend   │────▶│   Worker    │
│  React/Vite  │     │   FastAPI   │     │   Celery    │
│  Port 3000   │     │  Port 8080  │     │             │
└─────────────┘     └──────┬──────┘     └──────┬──────┘
                           │                    │
                           └────────┬───────────┘
                                    │
                              ┌─────▼─────┐
                              │   Redis    │
                              │ Port 6379  │
                              └───────────┘
```

## Quick Start

### Docker (Recommended)

```bash
docker-compose up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8080
- API Docs: http://localhost:8080/docs

### Manual Setup

#### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### Worker
```bash
cd backend
celery -A app.tasks worker --loglevel=info
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

#### Redis
```bash
docker run -d -p 6379:6379 redis:7-alpine
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/scrape | Scrape a Reddit URL |
| POST | /api/generate | Start video generation |
| GET | /api/jobs | List all jobs |
| GET | /api/jobs/{id} | Get job status |
| GET | /api/jobs/{id}/download | Download completed video |
| DELETE | /api/jobs/{id} | Delete a job |
| POST | /api/upload/background | Upload background video |
| POST | /api/upload/logo | Upload logo image |
| GET | /api/voices | List available TTS voices |

## Video Output

- **Resolution**: 1080x1920 (9:16 vertical)
- **Format**: H.264 MP4 with AAC audio
- **Features**: Reddit-style text cards, karaoke subtitles, logo overlay, background video

## Tech Stack

**Backend**: Python, FastAPI, Celery, Redis, BeautifulSoup4, Coqui TTS, faster-whisper, FFmpeg, Pillow

**Frontend**: React 18, Vite, TypeScript, Tailwind CSS, shadcn/ui, Lucide Icons, Framer Motion

## License

MIT
