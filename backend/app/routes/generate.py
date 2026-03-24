"""Video generation API endpoint."""

from fastapi import APIRouter, HTTPException

from app.models import GenerateRequest, JobInfo
from app.tasks import create_job, _get_job

router = APIRouter()


@router.post("/generate", response_model=JobInfo)
async def generate_video(request: GenerateRequest):
    """Start a new video generation job."""
    if not request.title.strip():
        raise HTTPException(status_code=400, detail="Title is required")
    if not request.body.strip():
        raise HTTPException(status_code=400, detail="Body text is required")

    subtitle_settings = None
    if request.subtitle_settings:
        subtitle_settings = request.subtitle_settings.model_dump()

    job_id = create_job(
        title=request.title.strip(),
        body=request.body.strip(),
        subreddit=request.subreddit or "",
        background_filename=request.background_filename,
        logo_filename=request.logo_filename,
        logo_position=request.logo_position.value,
        voice=request.voice,
        speed=request.speed,
        subtitle_settings=subtitle_settings,
    )

    job = _get_job(job_id)
    return JobInfo(
        id=job["id"],
        title=job["title"],
        status=job["status"],
        progress=float(job.get("progress", 0)),
        created_at=job["created_at"],
    )
