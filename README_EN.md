# 🧙 MTG Scraper

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Changelog](https://img.shields.io/badge/changelog-0.2.0-blue.svg)](CHANGELOG.md)

[English](https://github.com/barrins-project/mtg_scraper/blob/main/README_EN.md) | [French](https://github.com/barrins-project/mtg_scraper/blob/main/README.md)

A modular and multithreaded scraper designed to fetch Magic: The Gathering tournament results from multiple sources, including **MTGO** and **MTGTop8**.
This project is built to be part of a data pipeline for statistical analysis and visualization, especially in competitive formats like **Duel Commander**, **EDH**, or **Modern**.

## 📦 Features

- 🔎 Tournament scraping from:
  - [x] MTGO (via multithreaded HTML scraping with Chrome browser emulation)
  - [x] MTGTop8 (via multithreaded HTML scraping)
- 📅 Format and date-range filtering (`Standard`, `Modern`, `Duel Commander`, etc.)
- 📂 Output in standardized JSON format
- 🧵 Parallel downloads to speed up scraping
- 🧪 Ready for backend integration (FastAPI) and machine learning pipelines
- ⏱️ MTGO scraping driven by explicit Selenium waits (`WebDriverWait`) instead
  of fixed `sleep()` calls: the scraper waits for the page to actually finish
  rendering, with a growing timeout on subsequent retries when rendering is
  slow

## 🚀 Usage

### 1. Clone and Install

Make sure Python 3.10+ is installed, then run:

```bash
git clone https://github.com/barrins-project/mtg_scraper.git
cd mtg_scraper
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows
pip install .
```

### 2. Run via CLI

You can launch scraping with either of the following commands:

```bash
python -m scraper --source mtgtop8 --date-from 2024-05 --date-to 2024-12
scrape --source mtgtop8 --date-from 2024-05 --date-to 2024-12
```

#### Options

| Parameter     | Description                                          | Default Value |
| ------------- | ---------------------------------------------------- | ------------- |
| `--source`    | Source to scrape: `mtgo` or `mtgtop8`                | `mtgo`        |
| `--date-from` | Start date (`YYYY-MM` format) *(**MTGO** only)*      | 5 days ago    |
| `--date-to`   | End date (`YYYY-MM` format) *(**MTGO** only)         | Today         |
| `--force-mtgo`| Force recraping *(**MTGO** only)                     | False         |
| `--span`      | Number of tournaments to inspect *(**MTGTOP8** only) | 1000          |

### 3. Example in Code

```python
from datetime import datetime
from scraper import services

# Download tournaments from April 2024
services.scrape_mtgtop8(datetime(2024, 4, 1).date())
```

Currently, scraping is not limited to a specific format within a source.

## 🧪 Tests

Test suite is coming soon — contributions are welcome!

## 📝 Changelog

Notable changes for each version are documented in
[CHANGELOG.md](CHANGELOG.md), which follows [Keep a
Changelog](https://keepachangelog.com/en/1.1.0/) and [Semantic
Versioning](https://semver.org/).

## 📈 Recommended Integration

This scraper is intended to feed a Magic deck analysis pipeline (using a database + FastAPI backend).
It can be run periodically via a `cronjob` or triggered from an admin interface.

## 🤝 Contributing

We welcome contributions! To propose improvements:

1. Fork the repository
2. Create a branch `feature/your-feature-name`
3. Open a Pull Request ✨

## 📜 License

MIT — free to reuse and adapt in your own projects.

---

**Parent project:** [barrins-project](https://github.com/barrins-project)
For questions, reach out via GitHub or Discord.
