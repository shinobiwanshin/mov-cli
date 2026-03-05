# 🎬 mov-cli

A terminal-based movie search and streaming tool inspired by [ani-cli](https://github.com/pystardust/ani-cli). Search for movies, pick one, and stream it — all from the command line.

---

## Features

- **Search** movies directly from the terminal via IMDb.
- **Select** your movie interactively from a numbered list.
- **Stream** instantly using `vidsrc.cc`.
- **Player Integration**: Automatically extracts `.m3u8` streams and plays them directly in **IINA**.

## Installation

You can install `mov-cli` directly from this repository in "editable" mode:

```bash
git clone https://github.com/yourusername/mov-cli.git
cd mov-cli
pip install -e .
```

## Usage

Simply run `mov-cli` followed by the movie name you want to search for:

```bash
mov-cli interstellar
```

### Options

```
usage: mov-cli [-h] [-v] query [query ...]

positional arguments:
  query          Movie title to search for

options:
  -h, --help     show this help message and exit
  -v, --version  show program's version number and exit
```

## Architecture

`mov-cli` uses an `ani-cli` style architecture:

1. **Scrape Search**: Queries IMDb for movie suggestions/data.
2. **Select**: Interactive terminal menu using `rich`.
3. **Extract Stream**: Fetches the `vidsrc.cc` embed page, extracts the provider iframe, and resolves the underlying `.m3u8` file.
4. **Play**: Launches the direct stream in `IINA` via subprocess.

## Project Structure

```text
mov-cli/
    mov_cli/
        __init__.py
        cli.py
        imdb_search.py
        stream_extractor.py
        player.py
        utils.py
    main.py
    requirements.txt
    README.md
```

## Next Features (Planned)

Structure is ready for:

- Fuzzy search (fzf)
- Watch history
- TV show support
- Multiple streaming providers
- Subtitles support (`--sub-auto=fuzzy`)
