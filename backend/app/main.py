"""FastAPI application for Reddit Video Generator."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.routes import scrape, generate, jobs, uploads

app = FastAPI(
    title="Reddit Video Generator",
    description="Generate Reddit-style short-form videos with TTS narration and karaoke subtitles",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(scrape.router, prefix="/api", tags=["Scraping"])
app.include_router(generate.router, prefix="/api", tags=["Generation"])
app.include_router(jobs.router, prefix="/api", tags=["Jobs"])
app.include_router(uploads.router, prefix="/api", tags=["Uploads"])

# Serve storage files
app.mount("/storage", StaticFiles(directory=settings.STORAGE_PATH), name="storage")


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "version": "1.0.0"}
