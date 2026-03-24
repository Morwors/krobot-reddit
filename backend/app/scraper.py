"""Reddit post scraper using old.reddit.com for easier parsing."""

import re
import random
import requests
from bs4 import BeautifulSoup
from app.models import ScrapedPost

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0",
]


def _convert_to_old_reddit(url: str) -> str:
    """Convert any Reddit URL to old.reddit.com format."""
    url = url.strip()
    url = re.sub(r'https?://(www\.)?reddit\.com', 'https://old.reddit.com', url)
    url = re.sub(r'https?://new\.reddit\.com', 'https://old.reddit.com', url)
    if 'old.reddit.com' not in url and 'reddit.com' in url:
        url = url.replace('reddit.com', 'old.reddit.com')
    # Remove query params
    url = url.split('?')[0]
    # Ensure .json is not appended
    url = url.rstrip('/')
    return url


def _parse_score(score_text: str) -> int:
    """Parse Reddit score text like '1.2k' or '•' into integer."""
    if not score_text or score_text == '•':
        return 0
    score_text = score_text.strip().lower().replace(',', '')
    if 'k' in score_text:
        return int(float(score_text.replace('k', '')) * 1000)
    if 'm' in score_text:
        return int(float(score_text.replace('m', '')) * 1000000)
    try:
        return int(score_text)
    except ValueError:
        return 0


def scrape_reddit_post(url: str) -> ScrapedPost:
    """Scrape a Reddit post from its URL."""
    old_url = _convert_to_old_reddit(url)

    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "DNT": "1",
        "Connection": "keep-alive",
    }

    # Try JSON endpoint first (most reliable)
    json_url = old_url + ".json"
    try:
        resp = requests.get(json_url, headers=headers, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, list) and len(data) > 0:
                post_data = data[0]["data"]["children"][0]["data"]
                return ScrapedPost(
                    title=post_data.get("title", ""),
                    selftext=post_data.get("selftext", ""),
                    subreddit=post_data.get("subreddit", ""),
                    author=post_data.get("author", "[deleted]"),
                    score=post_data.get("score", 0),
                    num_comments=post_data.get("num_comments", 0),
                    url=url,
                )
    except (requests.RequestException, ValueError, KeyError, IndexError):
        pass

    # Fallback: HTML scraping
    resp = requests.get(old_url, headers=headers, timeout=15)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "lxml")

    # Title
    title_elem = soup.find("a", class_="title")
    title = title_elem.get_text(strip=True) if title_elem else ""

    # Selftext (post body)
    selftext_div = soup.find("div", class_="usertext-body")
    if selftext_div:
        # Get text content, preserving paragraph breaks
        paragraphs = selftext_div.find_all("p")
        if paragraphs:
            selftext = "\n\n".join(p.get_text(strip=True) for p in paragraphs)
        else:
            selftext = selftext_div.get_text(strip=True)
    else:
        selftext = ""

    # Subreddit
    subreddit_elem = soup.find("span", class_="hover", string=re.compile(r"r/"))
    if not subreddit_elem:
        subreddit_elem = soup.find("a", class_="subreddit")
    subreddit = ""
    if subreddit_elem:
        sub_text = subreddit_elem.get_text(strip=True)
        subreddit = sub_text.replace("r/", "")
    else:
        # Extract from URL
        match = re.search(r'/r/(\w+)', url)
        if match:
            subreddit = match.group(1)

    # Author
    author_elem = soup.find("a", class_=re.compile(r"author"))
    author = author_elem.get_text(strip=True) if author_elem else "[deleted]"

    # Score
    score_elem = soup.find("div", class_="score")
    if score_elem:
        score_text = score_elem.find("span", class_="number")
        score = _parse_score(score_text.get_text() if score_text else "0")
    else:
        score_elem = soup.find("span", class_="score")
        score = _parse_score(score_elem.get_text() if score_elem else "0")

    # Comments count
    comments_elem = soup.find("a", class_="comments")
    num_comments = 0
    if comments_elem:
        match = re.search(r'(\d+)', comments_elem.get_text())
        if match:
            num_comments = int(match.group(1))

    return ScrapedPost(
        title=title,
        selftext=selftext,
        subreddit=subreddit,
        author=author,
        score=score,
        num_comments=num_comments,
        url=url,
    )
