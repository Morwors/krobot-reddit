"""Reddit scraping API endpoint."""

from fastapi import APIRouter, HTTPException

from app.models import ScrapeRequest, ScrapedPost
from app.scraper import scrape_reddit_post

router = APIRouter()


@router.post("/scrape", response_model=ScrapedPost)
async def scrape_post(request: ScrapeRequest):
    """Scrape a Reddit post from its URL and return extracted data."""
    try:
        post = scrape_reddit_post(request.url)
        if not post.title:
            raise HTTPException(status_code=404, detail="Could not extract post data from the given URL")
        return post
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")
