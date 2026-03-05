"""
Utility functions and configuration constants for mov-cli.
"""

from rich.console import Console

# ── IMDb Configuration ────────────────────────────────────────────────────────
IMDB_SEARCH_URL = "https://www.imdb.com/find/?q={query}"

# ── HTTP Headers ───────────────────────────────────────────────────────────────
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

console = Console()


def format_year(year) -> str:
    """
    Format a year value for display.

    Args:
        year: An int year, a string, or None.

    Returns:
        The year as a string, or "N/A" if unavailable.
    """
    if year is not None:
        return str(year)
    return "N/A"
