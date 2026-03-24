"""Pydantic models for request/response schemas."""

from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime


class LogoPosition(str, Enum):
    TOP_LEFT = "top-left"
    TOP_RIGHT = "top-right"
    BOTTOM_LEFT = "bottom-left"
    BOTTOM_RIGHT = "bottom-right"


class JobStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    DONE = "done"
    FAILED = "failed"


# ── Scrape ──────────────────────────────────────────────────────────

class ScrapeRequest(BaseModel):
    url: str = Field(..., description="Reddit post URL to scrape")


class ScrapedPost(BaseModel):
    title: str
    selftext: str
    subreddit: str
    author: str
    score: int
    num_comments: int
    url: str


# ── Generation ──────────────────────────────────────────────────────

class SubtitleSettings(BaseModel):
    font_size: int = 48
    text_color: str = "#FFFFFF"
    highlight_color: str = "#FFFF00"
    bg_opacity: float = 0.7


class GenerateRequest(BaseModel):
    title: str = Field(..., description="Video title / Reddit post title")
    body: str = Field(..., description="Script text / Reddit post body")
    subreddit: Optional[str] = Field(None, description="Subreddit name for badge")
    background_filename: Optional[str] = Field(None, description="Uploaded background video filename")
    logo_filename: Optional[str] = Field(None, description="Uploaded logo filename")
    logo_position: LogoPosition = LogoPosition.TOP_RIGHT
    voice: str = Field("p226", description="TTS voice/speaker ID")
    speed: float = Field(1.0, ge=0.5, le=2.0)
    subtitle_settings: Optional[SubtitleSettings] = None


# ── Jobs ────────────────────────────────────────────────────────────

class JobInfo(BaseModel):
    id: str
    title: str
    status: JobStatus
    progress: float = 0.0
    created_at: str
    completed_at: Optional[str] = None
    error: Optional[str] = None
    output_filename: Optional[str] = None
    duration: Optional[float] = None


class JobListResponse(BaseModel):
    jobs: List[JobInfo]


# ── Uploads ─────────────────────────────────────────────────────────

class UploadResponse(BaseModel):
    filename: str
    original_name: str
    size: int


# ── Voices ──────────────────────────────────────────────────────────

class VoiceInfo(BaseModel):
    id: str
    name: str
    gender: str
    description: str


class VoiceListResponse(BaseModel):
    voices: List[VoiceInfo]
