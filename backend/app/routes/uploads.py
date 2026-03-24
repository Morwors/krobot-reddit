"""File upload and voice listing API endpoints."""

import os
import uuid
import shutil
from typing import List

from fastapi import APIRouter, HTTPException, UploadFile, File

from app.models import UploadResponse, VoiceListResponse
from app.config import settings
from app.tts_engine import list_voices

router = APIRouter()

ALLOWED_VIDEO_TYPES = {
    "video/mp4", "video/webm", "video/quicktime", "video/x-msvideo",
    "video/x-matroska", "video/mpeg", "application/octet-stream",
}
ALLOWED_IMAGE_TYPES = {
    "image/png", "image/jpeg", "image/gif", "image/webp", "image/svg+xml",
    "application/octet-stream",
}
MAX_VIDEO_SIZE = 500 * 1024 * 1024  # 500MB
MAX_IMAGE_SIZE = 10 * 1024 * 1024   # 10MB


async def _save_upload(
    file: UploadFile,
    destination_dir: str,
    allowed_types: set,
    max_size: int,
) -> UploadResponse:
    """Save an uploaded file to the destination directory."""
    content_type = file.content_type or "application/octet-stream"

    # Determine extension from original filename
    original_name = file.filename or "upload"
    _, ext = os.path.splitext(original_name)
    if not ext:
        ext = ".mp4" if "video" in content_type else ".png"

    # Generate unique filename
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(destination_dir, filename)

    # Read and save file
    content = await file.read()
    size = len(content)

    if size > max_size:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {max_size // (1024*1024)}MB",
        )

    os.makedirs(destination_dir, exist_ok=True)
    with open(filepath, "wb") as f:
        f.write(content)

    return UploadResponse(
        filename=filename,
        original_name=original_name,
        size=size,
    )


@router.post("/upload/background", response_model=UploadResponse)
async def upload_background(file: UploadFile = File(...)):
    """Upload a background video file."""
    return await _save_upload(
        file,
        settings.BACKGROUNDS_PATH,
        ALLOWED_VIDEO_TYPES,
        MAX_VIDEO_SIZE,
    )


@router.post("/upload/logo", response_model=UploadResponse)
async def upload_logo(file: UploadFile = File(...)):
    """Upload a logo image file."""
    return await _save_upload(
        file,
        settings.LOGOS_PATH,
        ALLOWED_IMAGE_TYPES,
        MAX_IMAGE_SIZE,
    )


@router.get("/voices", response_model=VoiceListResponse)
async def get_voices():
    """List available TTS voices."""
    voices = list_voices()
    return VoiceListResponse(voices=voices)
