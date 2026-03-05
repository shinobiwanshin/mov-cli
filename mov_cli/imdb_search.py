"""
IMDb search module — scrapes movie search results from IMDb.
"""

import re
import requests
from bs4 import BeautifulSoup

from mov_cli.utils import HEADERS, IMDB_SEARCH_URL


def search_imdb(query: str) -> list[dict]:
    """
    Search IMDb using their suggestion API (JSON endpoint).

    Args:
        query: The movie title to search for.

    Returns:
        A list of dicts with keys: title, year, imdb_id, stars.
    """
    url = f"https://v2.sg.media-imdb.com/suggests/{query[0].lower()}/{query.replace(' ', '_')}.json"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        text = response.text

        # The response is JSONP: imdb$query({"d":[...]})
        json_str = re.search(r'\(({.*})\)', text)
        if not json_str:
            return []

        import json
        data = json.loads(json_str.group(1))
        results = []

        for item in data.get("d", []):
            # Only include movies (feature films)
            qid = item.get("qid", "")
            if qid not in ("movie", "tvMovie", "short", "video"):
                continue

            imdb_id = item.get("id", "")
            if not imdb_id.startswith("tt"):
                continue

            results.append({
                "title": item.get("l", "Unknown"),
                "year": item.get("y"),
                "imdb_id": imdb_id,
                "stars": item.get("s", ""),
            })

        return results

    except (requests.RequestException, ValueError):
        return []


def search_imdb_scrape(query: str) -> list[dict]:
    """
    Fallback: scrape IMDb's HTML search page.

    Args:
        query: The movie title to search for.

    Returns:
        A list of dicts with keys: title, year, imdb_id, stars.
    """
    url = IMDB_SEARCH_URL.format(query=query.replace(" ", "+"))
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        results = []

        # IMDb's modern search page uses JSON-LD or specific selectors
        for item in soup.select("li.find-title-result, li.find-result-item"):
            link = item.select_one("a[href*='/title/']")
            if not link:
                continue

            href = link.get("href", "")
            match = re.search(r"(tt\d+)", href)
            if not match:
                continue

            imdb_id = match.group(1)
            title_text = link.get_text(strip=True)

            # Try to extract year
            year = None
            year_match = re.search(r"\((\d{4})\)", item.get_text())
            if year_match:
                year = int(year_match.group(1))

            # Try to extract stars/cast
            stars = ""
            stars_el = item.select_one(".ipc-metadata-list-summary-item__tl")
            if stars_el:
                stars = stars_el.get_text(strip=True)

            results.append({
                "title": title_text,
                "year": year,
                "imdb_id": imdb_id,
                "stars": stars,
            })

        return results

    except requests.RequestException:
        return []
