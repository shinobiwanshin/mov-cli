# Contributing to mov-cli

Thank you for your interest in contributing to **mov-cli**! Contributions of all kinds are welcome — bug reports, feature requests, documentation improvements, and code changes.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting Features](#suggesting-features)
  - [Submitting Code Changes](#submitting-code-changes)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Style Guide](#style-guide)
- [Commit Messages](#commit-messages)

---

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold a respectful, inclusive environment for everyone.

---

## Getting Started

1. **Fork** the repository on GitHub.
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/<your-username>/mov-cli.git
   cd mov-cli
   ```
3. **Create a branch** for your change:
   ```bash
   git checkout -b feat/my-new-feature
   ```
4. Make your changes, then **push** and open a **Pull Request**.

---

## How to Contribute

### Reporting Bugs

Found something broken? Please [open a bug report](.github/ISSUE_TEMPLATE/bug_report.md) and include:

- A clear title and description.
- Steps to reproduce the issue.
- What you expected vs. what actually happened.
- Your OS, Python version, and any relevant output or error messages.

### Suggesting Features

Have an idea? [Open a feature request](.github/ISSUE_TEMPLATE/feature_request.md) with:

- A description of the problem the feature would solve.
- A proposed solution or implementation idea (optional).

### Submitting Code Changes

1. Make sure your code follows the [Style Guide](#style-guide).
2. Write or update tests where applicable.
3. Run the tests locally before submitting.
4. Open a Pull Request against the `main` branch using our [PR template](.github/PULL_REQUEST_TEMPLATE.md).

---

## Development Setup

### Prerequisites

- Python 3.9 or newer
- `pip`

### Install in editable mode

```bash
pip install -e .
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run the CLI

```bash
mov-cli <movie title>
# or
python main.py <movie title>
```

---

## Project Structure

```text
mov-cli/
├── mov_cli/
│   ├── __init__.py
│   ├── cli.py             # Argument parsing & entry point
│   ├── imdb_search.py     # IMDb search scraping
│   ├── stream_extractor.py# Stream URL extraction
│   ├── player.py          # Media player integration
│   ├── history.py         # Watch history
│   ├── utils.py           # Shared utilities
│   └── providers/         # Streaming provider modules
├── main.py
├── requirements.txt
├── setup.py
└── README.md
```

---

## Style Guide

- Follow [PEP 8](https://peps.python.org/pep-0008/) for Python code.
- Use descriptive variable and function names.
- Keep functions small and focused on a single responsibility.
- Add docstrings to public functions and classes.

---

## Commit Messages

Use clear, concise commit messages in the imperative mood:

```
feat: add TV show support
fix: handle missing stream URL gracefully
docs: update installation instructions
refactor: simplify provider selection logic
```

Common prefixes: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`.
