"""
CLI entry point — handles arguments, user interaction, and orchestration.

Flow: search → select → extract stream → play
      or: -c → pick from history → extract stream → play
"""

import argparse
import sys

from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt

from mov_cli import __version__
from mov_cli.utils import console, format_year
from mov_cli.imdb_search import search_imdb, search_imdb_scrape
from mov_cli.stream_extractor import get_stream
from mov_cli.player import play_in_iina, play_in_browser
from mov_cli.history import (
    add_to_history,
    get_history,
    remove_from_history,
    clear_history,
    download_subtitle,
    find_iina_subtitle,
    cleanup_temp_subs,
)


def build_parser() -> argparse.ArgumentParser:
    """Build and return the argument parser."""
    parser = argparse.ArgumentParser(
        prog="mov-cli",
        description="🎬 Search and stream movies from the terminal.",
        epilog="Example:  mov-cli interstellar",
    )
    parser.add_argument(
        "query",
        nargs="*",
        help="Movie title to search for",
    )
    parser.add_argument(
        "-c", "--continue",
        action="store_true",
        dest="continue_watching",
        help="Continue watching from history",
    )
    parser.add_argument(
        "-d", "--delete-history",
        action="store_true",
        help="Clear all watch history",
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def display_results(movies: list[dict]) -> None:
    """Print a rich table of search results."""
    table = Table(
        title="🎬 Search Results",
        show_header=True,
        header_style="bold magenta",
        border_style="bright_black",
        title_style="bold white",
        padding=(0, 1),
    )
    table.add_column("#", style="bold yellow", justify="right", width=4)
    table.add_column("Title", style="bold white", min_width=30)
    table.add_column("Year", style="cyan", justify="center", width=6)
    table.add_column("Cast", style="dim", max_width=45, no_wrap=True)

    for idx, movie in enumerate(movies, start=1):
        year = format_year(movie.get("year"))
        title = movie.get("title", "Unknown")
        stars = movie.get("stars", "")
        if len(stars) > 45:
            stars = stars[:42] + "..."
        table.add_row(str(idx), title, year, stars)

    console.print()
    console.print(table)


def display_history(entries: list[dict]) -> None:
    """Print a rich table of watch history."""
    table = Table(
        title="📜 Watch History",
        show_header=True,
        header_style="bold magenta",
        border_style="bright_black",
        title_style="bold white",
        padding=(0, 1),
    )
    table.add_column("#", style="bold yellow", justify="right", width=4)
    table.add_column("Title", style="bold white", min_width=30)
    table.add_column("Year", style="cyan", justify="center", width=6)
    table.add_column("Last Watched", style="dim", max_width=20)

    for idx, entry in enumerate(entries, start=1):
        last = entry.get("last_watched", "")[:10]  # just the date
        table.add_row(
            str(idx),
            entry.get("title", "Unknown"),
            str(entry.get("year", "N/A")),
            last,
        )

    console.print()
    console.print(table)


def prompt_selection(total: int) -> int:
    """Prompt the user to select by number."""
    while True:
        console.print()
        try:
            raw = Prompt.ask("[bold white]Select movie[/bold white]")
            choice = int(raw)
        except (ValueError, EOFError):
            console.print("[yellow]Please enter a valid number.[/yellow]")
            continue

        if 1 <= choice <= total:
            return choice - 1

        console.print(f"[yellow]Please pick a number between 1 and {total}.[/yellow]")


def play_movie(imdb_id: str, title: str, year: str) -> None:
    """Handle player selection, extraction, and playback for a movie."""

    # ── Choose Player ────────────────────────────────────────────────────
    while True:
        console.print()
        raw = Prompt.ask("[bold white]Play in (1) IINA or (2) Browser?[/bold white]")
        if raw in ["1", "2"]:
            player_choice = raw
            break
        console.print("[yellow]Please enter 1 or 2.[/yellow]")

    if player_choice == "2":
        embed_url = f"https://vidsrc.icu/embed/movie/{imdb_id}"
        console.print(f"\n[bold green]▶[/bold green]  Opening [bold cyan]Browser[/bold cyan]...")
        play_in_browser(embed_url)
        add_to_history(imdb_id, title, year)
        return

    # ── Extract Stream (IINA only) ───────────────────────────────────────
    try:
        result = get_stream(imdb_id)
    except Exception as e:
        console.print(f"[bold red]Extraction failed:[/bold red] {e}")
        sys.exit(1)

    stream_url = result["stream"]
    subtitle_url = result.get("subtitle")

    # Download subtitle locally for persistence
    local_sub = None
    if subtitle_url:
        console.print(f"[bold green]✓[/bold green] Subtitles found! Downloading...")
        local_sub = download_subtitle(subtitle_url, imdb_id)
        if local_sub:
            console.print(f"[dim]Saved to {local_sub}[/dim]")

    # ── Play ──────────────────────────────────────────────────────────────
    console.print(f"\n[bold green]▶[/bold green]  Launching [bold cyan]IINA[/bold cyan]...")
    play_in_iina(stream_url, title=f"{title} ({year})", subtitle=local_sub)

    # Save to history with cached stream and local subtitle
    add_to_history(imdb_id, title, year, stream=stream_url, subtitle=local_sub)

    # Always check if IINA downloaded a subtitle during playback
    iina_sub = find_iina_subtitle(imdb_id)
    if iina_sub:
        console.print(f"[bold green]✓[/bold green] IINA subtitle saved to ~/Documents/subtitles/")
        add_to_history(imdb_id, title, year, stream=stream_url, subtitle=iina_sub)

    # ── Finished? ─────────────────────────────────────────────────────────
    console.print()
    finished = Prompt.ask(
        "[bold white]Finished watching? Remove from history?[/bold white]",
        choices=["y", "n"],
        default="n",
    )
    if finished == "y":
        remove_from_history(imdb_id)
        cleanup_temp_subs()
        console.print("[dim]Removed from history. Temp subtitles cleaned.[/dim]")


def main() -> None:
    """Main CLI entry point."""
    parser = build_parser()
    args = parser.parse_args()

    # ── Delete History ────────────────────────────────────────────────────
    if args.delete_history:
        clear_history()
        console.print("[bold green]✓[/bold green] Watch history cleared.")
        sys.exit(0)

    # ── Continue Watching ─────────────────────────────────────────────────
    if args.continue_watching:
        entries = get_history()
        if not entries:
            console.print(
                Panel(
                    "[yellow]No watch history yet.[/yellow]\n"
                    "[dim]Watch a movie first![/dim]",
                    border_style="yellow",
                    title="Empty History",
                )
            )
            sys.exit(0)

        display_history(entries)
        selection = prompt_selection(len(entries))
        selected = entries[selection]

        title = selected["title"]
        year = str(selected.get("year", "N/A"))
        imdb_id = selected["imdb_id"]

        cached_stream = selected.get("stream")
        cached_sub = selected.get("subtitle")

        console.print(
            f"\n[bold green]✓[/bold green]  Continuing: [bold]{title}[/bold] ({year})"
        )

        # If we have a cached stream, offer to use it directly
        if cached_stream:
            console.print(f"[dim]Cached stream available.[/dim]")
            use_cached = Prompt.ask(
                "[bold white]Use cached stream? (skip browser)[/bold white]",
                choices=["y", "n"],
                default="y",
            )
            if use_cached == "y":
                console.print(f"\n[bold green]▶[/bold green]  Launching [bold cyan]IINA[/bold cyan]...")
                play_in_iina(cached_stream, title=f"{title} ({year})", subtitle=cached_sub)

                console.print()
                finished = Prompt.ask(
                    "[bold white]Finished watching? Remove from history?[/bold white]",
                    choices=["y", "n"],
                    default="n",
                )
                if finished == "y":
                    remove_from_history(imdb_id)
                    console.print("[dim]Removed from history.[/dim]")
                sys.exit(0)

        play_movie(imdb_id, title, year)
        sys.exit(0)

    # ── Search ────────────────────────────────────────────────────────────
    if args.query:
        query = " ".join(args.query)
    else:
        query = Prompt.ask("[bold cyan]🎬 Search movie[/bold cyan]")
        if not query.strip():
            sys.exit(0)

    with console.status(
        f"[bold cyan]Searching for \"{query}\"...[/bold cyan]",
        spinner="dots",
    ):
        movies = search_imdb(query)
        if not movies:
            movies = search_imdb_scrape(query)

    if not movies:
        console.print(
            Panel(
                f"[yellow]No results found for[/yellow] [bold]\"{query}\"[/bold].\n"
                "[dim]Try a different search term.[/dim]",
                border_style="yellow",
                title="No Results",
            )
        )
        sys.exit(0)

    movies = movies[:15]

    # ── Display & Select ──────────────────────────────────────────────────
    display_results(movies)
    selection = prompt_selection(len(movies))
    selected = movies[selection]

    title = selected.get("title", "Unknown")
    year = format_year(selected.get("year"))
    imdb_id = selected["imdb_id"]

    console.print(
        f"\n[bold green]✓[/bold green]  Selected: [bold]{title}[/bold] ({year})  "
        f"[dim]IMDb: {imdb_id}[/dim]"
    )

    play_movie(imdb_id, title, year)


if __name__ == "__main__":
    main()
