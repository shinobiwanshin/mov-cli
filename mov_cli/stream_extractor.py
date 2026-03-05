"""
Stream extraction module.
Launches Chrome normally (no automation flags), connects via CDP
to intercept .m3u8 and subtitle network traffic while you click play.
"""

import subprocess
import time
import random
import os
from playwright.sync_api import sync_playwright
from mov_cli.utils import console


VIDSRC_EMBED = "https://vidsrc.icu/embed/movie/{imdb_id}"
CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def get_stream(imdb_id: str) -> dict:
    """
    Launch Chrome, connect via CDP, capture .m3u8 and subtitle URLs.

    Returns:
        dict with keys: "stream" (str), "subtitle" (str | None)
    """
    embed_url = VIDSRC_EMBED.format(imdb_id=imdb_id)
    captured_streams: list[str] = []
    captured_subs: list[str] = []

    # Use a random port to avoid conflicts with existing Chrome instances
    cdp_port = random.randint(9300, 9399)

    console.print(
        "\n[bold cyan]🌐 Opening browser...[/bold cyan]\n"
        "[dim]Click the play button to start the video.[/dim]\n"
        "[dim]Stream & subtitles will be captured automatically.[/dim]\n"
    )

    tmp_profile = f"/tmp/mov-cli-chrome-{os.getpid()}"

    chrome_proc = subprocess.Popen(
        [
            CHROME_PATH,
            f"--remote-debugging-port={cdp_port}",
            f"--user-data-dir={tmp_profile}",
            "--no-first-run",
            "--no-default-browser-check",
            "--window-size=1024,640",
            embed_url,
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # Retry CDP connection — Chrome takes a moment to start
    browser = None
    try:
        with sync_playwright() as p:
            for attempt in range(10):
                time.sleep(2)
                try:
                    browser = p.chromium.connect_over_cdp(f"http://localhost:{cdp_port}")
                    break
                except Exception:
                    if attempt == 9:
                        raise
                    continue

            context = browser.contexts[0]
            page = context.pages[0] if context.pages else context.new_page()

            def on_request(request):
                url = request.url
                # Capture streams
                if ".m3u8" in url:
                    captured_streams.append(url)
                elif ".mp4" in url and "image" not in url and "poster" not in url:
                    captured_streams.append(url)
                # Capture subtitles
                if ".vtt" in url or ".srt" in url:
                    captured_subs.append(url)

            page.on("request", on_request)

            console.print("[yellow]⏳ Waiting for you to click play...[/yellow]")
            max_wait = 120
            waited = 0

            while not captured_streams and waited < max_wait:
                page.wait_for_timeout(2000)
                waited += 2

            if captured_streams:
                sub_msg = ""
                if captured_subs:
                    sub_msg = " [dim](+ subtitles)[/dim]"
                console.print(f"[bold green]✓[/bold green] Stream captured!{sub_msg}")
            else:
                console.print("[bold red]✗[/bold red] Timed out waiting for stream.")

            browser.close()

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
    finally:
        try:
            chrome_proc.terminate()
            chrome_proc.wait(timeout=5)
        except Exception:
            chrome_proc.kill()
        subprocess.run(["rm", "-rf", tmp_profile], capture_output=True)

    if not captured_streams:
        raise Exception(
            "No stream captured. Make sure to click play in the browser.\n"
            "Try option (2) Browser to watch directly instead."
        )

    # Deduplicate
    stream = _pick_best(captured_streams)
    subtitle = _pick_best(captured_subs) if captured_subs else None

    return {"stream": stream, "subtitle": subtitle}


def _pick_best(urls: list[str]) -> str:
    """Deduplicate and pick the best URL (prefer .m3u8)."""
    seen = []
    for u in urls:
        if u not in seen:
            seen.append(u)
    m3u8 = [s for s in seen if ".m3u8" in s]
    return m3u8[0] if m3u8 else seen[0]
