"""
Video player module — launches streams in IINA or browser.
"""

import subprocess
import sys
import webbrowser

from mov_cli.utils import console


def play_in_iina(url: str, title: str = "mov-cli Stream", subtitle: str | None = None) -> None:
    """
    Play a stream URL directly in IINA.

    Args:
        url: A video stream URL (.m3u8 or .mp4).
        title: The title to display in the player.
        subtitle: Optional subtitle URL (.vtt or .srt).
    """
    iina_cli = "/Applications/IINA.app/Contents/MacOS/iina-cli"

    args = [
        iina_cli,
        "--no-stdin",
        "--keep-running",
        f"--mpv-force-media-title={title}",
    ]

    if subtitle:
        args.append(f"--mpv-sub-file={subtitle}")

    args.append(url)

    try:
        subprocess.run(args, check=True)
    except FileNotFoundError:
        console.print(
            "[bold red]Error:[/bold red] Could not find the IINA CLI binary at:\n"
            f"[dim]{iina_cli}[/dim]\n"
            "Are you running on macOS and is IINA installed in /Applications?"
        )
        sys.exit(1)
    except subprocess.CalledProcessError:
        console.print(
            "[bold red]Error:[/bold red] Failed to launch IINA. "
            "Make sure IINA is installed.\n"
            "   [dim]brew install --cask iina[/dim]"
        )
        sys.exit(1)


def play_in_browser(url: str) -> None:
    """Open a URL in the default web browser."""
    webbrowser.open(url)
