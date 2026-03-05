"""
Watch history module — tracks movies you've watched.
Stores history as JSON at ~/.local/state/mov-cli/history.json
"""

import json
import os
import glob
import shutil
import tempfile
import time
import requests
from datetime import datetime
from pathlib import Path


HIST_DIR = Path.home() / ".local" / "state" / "mov-cli"
HIST_FILE = HIST_DIR / "history.json"
SUBS_DIR = Path.home() / "Documents" / "subtitles"


def _ensure_dir() -> None:
    """Create the history and subs directories if they don't exist."""
    HIST_DIR.mkdir(parents=True, exist_ok=True)
    SUBS_DIR.mkdir(parents=True, exist_ok=True)


def _load() -> list[dict]:
    """Load history from disk."""
    if not HIST_FILE.exists():
        return []
    try:
        with open(HIST_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def _save(history: list[dict]) -> None:
    """Save history to disk."""
    _ensure_dir()
    with open(HIST_FILE, "w") as f:
        json.dump(history, f, indent=2)


def add_to_history(
    imdb_id: str,
    title: str,
    year: str,
    stream: str | None = None,
    subtitle: str | None = None,
) -> None:
    """Add or update a movie in watch history, including cached stream URL."""
    history = _load()

    # Update if already exists
    for entry in history:
        if entry["imdb_id"] == imdb_id:
            entry["last_watched"] = datetime.now().isoformat()
            if stream:
                entry["stream"] = stream
            if subtitle:
                entry["subtitle"] = subtitle
            _save(history)
            return

    # Add new entry
    history.append({
        "imdb_id": imdb_id,
        "title": title,
        "year": year,
        "stream": stream,
        "subtitle": subtitle,
        "last_watched": datetime.now().isoformat(),
    })
    _save(history)


def get_history() -> list[dict]:
    """Return all history entries, most recent first."""
    history = _load()
    history.sort(key=lambda x: x.get("last_watched", ""), reverse=True)
    return history


def remove_from_history(imdb_id: str) -> None:
    """Remove a movie from history and delete its cached subtitle."""
    history = _load()

    # Delete the cached subtitle file if it exists
    for entry in history:
        if entry["imdb_id"] == imdb_id:
            sub_path = entry.get("subtitle")
            if sub_path and os.path.exists(sub_path):
                os.remove(sub_path)
            break

    history = [e for e in history if e["imdb_id"] != imdb_id]
    _save(history)


def clear_history() -> None:
    """Wipe all history."""
    _save([])


def cleanup_temp_subs() -> None:
    """Delete all subtitle files from IINA's temp directory."""
    tmp_dir = tempfile.gettempdir()
    for ext in ("*.srt", "*.vtt", "*.ass"):
        for f in glob.glob(os.path.join(tmp_dir, ext)):
            try:
                os.remove(f)
            except OSError:
                pass


def download_subtitle(url: str, imdb_id: str) -> str | None:
    """
    Download a subtitle file from a URL and save it locally.

    Returns:
        Local file path, or None if download failed.
    """
    _ensure_dir()
    ext = ".srt" if ".srt" in url else ".vtt"
    local_path = SUBS_DIR / f"{imdb_id}{ext}"

    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        with open(local_path, "wb") as f:
            f.write(r.content)
        return str(local_path)
    except Exception:
        return None


def find_iina_subtitle(imdb_id: str, since_seconds: int = 300) -> str | None:
    """
    Find the most recently downloaded subtitle from IINA's temp directory.
    IINA downloads subs to the macOS temp folder (/var/folders/.../T/).

    Args:
        imdb_id: Used for naming the cached copy.
        since_seconds: Only consider files modified within this many seconds.

    Returns:
        Path to the cached subtitle, or None.
    """
    _ensure_dir()
    tmp_dir = tempfile.gettempdir()
    now = time.time()

    # Find all subtitle files in the temp directory
    candidates = []
    for ext in ("*.srt", "*.vtt", "*.ass"):
        for f in glob.glob(os.path.join(tmp_dir, ext)):
            mtime = os.path.getmtime(f)
            if now - mtime < since_seconds:
                candidates.append((mtime, f))

    if not candidates:
        return None

    # Pick the most recently modified subtitle
    candidates.sort(reverse=True)
    _, best = candidates[0]

    # Copy it to our persistent subs directory
    ext = os.path.splitext(best)[1]
    local_path = SUBS_DIR / f"{imdb_id}{ext}"
    shutil.copy2(best, local_path)
    return str(local_path)
