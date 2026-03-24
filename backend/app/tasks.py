"""Celery tasks for async video generation."""

import os
import json
import logging
import uuid
from datetime import datetime, timezone

from celery import Celery

from app.config import settings

logger = logging.getLogger(__name__)

celery_app = Celery(
    "reddit_vid_gen",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    result_expires=86400,  # 24 hours
    worker_prefetch_multiplier=1,
    task_acks_late=True,
)

# ── Redis job storage helpers ───────────────────────────────────────

def _get_redis():
    """Get a Redis connection."""
    import redis
    return redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)


def _save_job(job_id: str, data: dict):
    """Save job data to Redis."""
    r = _get_redis()
    r.hset(f"job:{job_id}", mapping={k: json.dumps(v) if isinstance(v, (dict, list)) else str(v) for k, v in data.items()})
    r.sadd("jobs", job_id)


def _update_job(job_id: str, **kwargs):
    """Update specific job fields."""
    r = _get_redis()
    mapping = {}
    for k, v in kwargs.items():
        if isinstance(v, (dict, list)):
            mapping[k] = json.dumps(v)
        else:
            mapping[k] = str(v)
    r.hset(f"job:{job_id}", mapping=mapping)


def _get_job(job_id: str) -> dict:
    """Get job data from Redis."""
    r = _get_redis()
    raw = r.hgetall(f"job:{job_id}")
    if not raw:
        return None
    result = {}
    for k, v in raw.items():
        try:
            result[k] = json.loads(v)
        except (json.JSONDecodeError, TypeError):
            result[k] = v
    return result


def _get_all_jobs() -> list:
    """Get all job IDs."""
    r = _get_redis()
    return list(r.smembers("jobs"))


def _delete_job(job_id: str):
    """Delete a job from Redis and its files."""
    r = _get_redis()
    job = _get_job(job_id)

    # Delete output file
    if job and job.get("output_filename"):
        output_path = os.path.join(settings.OUTPUT_PATH, job["output_filename"])
        if os.path.exists(output_path):
            os.remove(output_path)

    # Delete temp directory
    temp_dir = os.path.join(settings.TEMP_PATH, job_id)
    if os.path.exists(temp_dir):
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)

    r.delete(f"job:{job_id}")
    r.srem("jobs", job_id)


def create_job(
    title: str,
    body: str,
    subreddit: str = "",
    background_filename: str = None,
    logo_filename: str = None,
    logo_position: str = "top-right",
    voice: str = "p226",
    speed: float = 1.0,
    subtitle_settings: dict = None,
) -> str:
    """Create a new video generation job and queue it."""
    job_id = str(uuid.uuid4())

    job_data = {
        "id": job_id,
        "title": title,
        "body": body,
        "subreddit": subreddit,
        "background_filename": background_filename or "",
        "logo_filename": logo_filename or "",
        "logo_position": logo_position,
        "voice": voice,
        "speed": speed,
        "subtitle_settings": subtitle_settings or {},
        "status": "queued",
        "progress": 0.0,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "completed_at": "",
        "error": "",
        "output_filename": "",
        "duration": 0.0,
    }

    _save_job(job_id, job_data)

    # Queue the Celery task
    generate_video_task.delay(job_id)

    logger.info(f"Job created and queued: {job_id}")
    return job_id


@celery_app.task(bind=True, name="generate_video")
def generate_video_task(self, job_id: str):
    """Main video generation Celery task."""
    from app.tts_engine import generate_tts_audio
    from app.subtitle_gen import generate_subtitle_data
    from app.video_composer import compose_video

    logger.info(f"Starting video generation for job {job_id}")

    job = _get_job(job_id)
    if not job:
        logger.error(f"Job {job_id} not found")
        return

    def update_progress(progress: float, message: str = ""):
        _update_job(job_id, status="processing", progress=round(progress, 2))
        self.update_state(state="PROGRESS", meta={"progress": progress, "message": message})

    try:
        _update_job(job_id, status="processing", progress=0.05)

        # Combine title and body for narration
        full_text = job["title"]
        body = job.get("body", "")
        if body:
            full_text += ". " + body

        # ── Step 1: Generate TTS audio ──────────────────────────────
        update_progress(0.1, "Generating narration audio...")
        voice = job.get("voice", "p226")
        speed = float(job.get("speed", 1.0))

        audio_path, audio_duration = generate_tts_audio(
            text=full_text,
            speaker=voice,
            speed=speed,
            job_id=job_id,
        )

        # ── Step 2: Generate subtitles ──────────────────────────────
        update_progress(0.3, "Generating subtitles...")
        subtitle_data = generate_subtitle_data(audio_path)

        # ── Step 3: Prepare file paths ──────────────────────────────
        background_path = None
        bg_filename = job.get("background_filename", "")
        if bg_filename:
            background_path = os.path.join(settings.BACKGROUNDS_PATH, bg_filename)
            if not os.path.exists(background_path):
                background_path = None

        logo_path = None
        logo_filename = job.get("logo_filename", "")
        if logo_filename:
            logo_path = os.path.join(settings.LOGOS_PATH, logo_filename)
            if not os.path.exists(logo_path):
                logo_path = None

        # Parse subtitle settings
        sub_settings = job.get("subtitle_settings", {})
        if isinstance(sub_settings, str):
            try:
                sub_settings = json.loads(sub_settings)
            except (json.JSONDecodeError, TypeError):
                sub_settings = {}

        # ── Step 4: Compose video ───────────────────────────────────
        update_progress(0.4, "Composing video...")

        output_path = compose_video(
            audio_path=audio_path,
            subtitle_data=subtitle_data,
            title=job["title"],
            body=body,
            subreddit=job.get("subreddit", ""),
            background_path=background_path,
            logo_path=logo_path,
            logo_position=job.get("logo_position", "top-right"),
            subtitle_settings=sub_settings,
            job_id=job_id,
            progress_callback=lambda p, msg: update_progress(0.4 + p * 0.55, msg),
        )

        output_filename = os.path.basename(output_path)

        _update_job(
            job_id,
            status="done",
            progress=1.0,
            completed_at=datetime.now(timezone.utc).isoformat(),
            output_filename=output_filename,
            duration=audio_duration,
        )

        logger.info(f"Job {job_id} completed successfully")

    except Exception as e:
        logger.exception(f"Job {job_id} failed: {e}")
        _update_job(
            job_id,
            status="failed",
            error=str(e),
            completed_at=datetime.now(timezone.utc).isoformat(),
        )
        raise
