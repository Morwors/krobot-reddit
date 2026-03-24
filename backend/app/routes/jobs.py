"""Job management API endpoints."""

import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.models import JobInfo, JobListResponse
from app.tasks import _get_job, _get_all_jobs, _delete_job
from app.config import settings

router = APIRouter()


def _job_to_info(job: dict) -> JobInfo:
    """Convert raw job dict to JobInfo model."""
    return JobInfo(
        id=job.get("id", ""),
        title=job.get("title", ""),
        status=job.get("status", "queued"),
        progress=float(job.get("progress", 0)),
        created_at=job.get("created_at", ""),
        completed_at=job.get("completed_at") or None,
        error=job.get("error") or None,
        output_filename=job.get("output_filename") or None,
        duration=float(job.get("duration", 0)) or None,
    )


@router.get("/jobs", response_model=JobListResponse)
async def list_jobs():
    """List all video generation jobs."""
    job_ids = _get_all_jobs()
    jobs = []
    for job_id in job_ids:
        job = _get_job(job_id)
        if job:
            jobs.append(_job_to_info(job))

    # Sort by created_at descending
    jobs.sort(key=lambda j: j.created_at or "", reverse=True)
    return JobListResponse(jobs=jobs)


@router.get("/jobs/{job_id}", response_model=JobInfo)
async def get_job(job_id: str):
    """Get status of a specific job."""
    job = _get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return _job_to_info(job)


@router.get("/jobs/{job_id}/download")
async def download_job(job_id: str):
    """Download the completed video for a job."""
    job = _get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.get("status") != "done":
        raise HTTPException(status_code=400, detail="Job is not completed yet")

    output_filename = job.get("output_filename")
    if not output_filename:
        raise HTTPException(status_code=404, detail="Output file not found")

    output_path = os.path.join(settings.OUTPUT_PATH, output_filename)
    if not os.path.exists(output_path):
        raise HTTPException(status_code=404, detail="Output file not found on disk")

    # Create a readable filename
    safe_title = "".join(c if c.isalnum() or c in " -_" else "" for c in job.get("title", "video"))[:50]
    download_name = f"{safe_title}.mp4"

    return FileResponse(
        output_path,
        media_type="video/mp4",
        filename=download_name,
    )


@router.delete("/jobs/{job_id}")
async def delete_job(job_id: str):
    """Delete a job and its associated files."""
    job = _get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    _delete_job(job_id)
    return {"message": "Job deleted", "id": job_id}
