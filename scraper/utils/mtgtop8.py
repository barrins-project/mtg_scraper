import json
import re
from pathlib import Path
from typing import Optional

from bs4 import BeautifulSoup

from scraper.parsers import mtgtop8 as parser
from scraper.parsers.mtgtop8 import get_tournament_soup as get_tournament_soup
from scraper.schemas import MTGScrape

# Tournament file naming convention:
# <tournament_id>_<sanitized_format>_<sanitized_tournament_name>.json

BASE_PATH = Path(__file__).resolve().parent.parent.parent / "scraped" / "mtgtop8.com"


def get_max_id_scraped() -> int:
    max_id = 0
    for file in BASE_PATH.rglob("*.json"):
        try:
            file_id = get_id_from_filepath(file)
            max_id = max(max_id, file_id)
        except ValueError:
            continue
    return max_id


def get_id_from_filepath(filepath: Path) -> int:
    return int(filepath.stem.split("_")[0])


def get_tournament_url(tournament_id: int) -> str:
    return f"https://mtgtop8.com/event?e={tournament_id}"


def we_should_scrape_it(tournament_url: str) -> bool:
    tournament_id = tournament_url.split("e=")[1]
    if "&" in tournament_id:
        tournament_id = tournament_id.split("&")[0]
    tournament_id = int(tournament_id)

    return tournament_id not in [
        int(f.stem.split("_")[0]) for f in BASE_PATH.glob("*.json") if f.is_file()
    ]


def scrape_tournament(url: str, soup: BeautifulSoup) -> Optional[MTGScrape]:
    tournament = parser.tournament(url, soup)
    if not tournament:
        print("❌ Element manquant dans les données du tournoi, extraction annulée.")
        return None

    tournament_date = tournament.date
    decks = parser.decks(soup)
    for deck in decks:
        deck.date = tournament_date

    return MTGScrape(
        tournament=tournament,
        decks=decks,
        rounds=[],  # MTGTOP8 does not provide round and standings data
        standings=[],  # MTGTOP8 does not provide round and standings data
    )


def save_tournament_scrape(scrape: MTGScrape) -> None:
    # Generating the file name
    tournament_name = scrape.tournament.name
    tournament_format = scrape.tournament.format
    tournament_id = scrape.tournament.url.split("e=")[1]
    if "&" in tournament_id:
        tournament_id = tournament_id.split("&")[0]

    filename = sanitize_string(f"{tournament_id}")
    filename = sanitize_string(f"{filename}_{tournament_format}")
    filename = sanitize_string(f"{filename}_{tournament_name}.json")

    # Getting the file path
    tournament_date = scrape.tournament.date
    year = str(tournament_date.year)
    month = f"{tournament_date.month:02}"
    day = f"{(tournament_date.day):02}"

    # Making sure that YYYY/MM/DD folder exists
    dir_path = BASE_PATH / year / month / day
    dir_path.mkdir(parents=True, exist_ok=True)

    file_path = Path(dir_path / filename)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(scrape.model_dump(mode="json"), f, ensure_ascii=False, indent=4)

    print(f"📂 Data saved in {file_path}")


def sanitize_string(string: str) -> str:
    string = string.lower()
    string = re.sub(r"[^a-z0-9_.]+", "-", string)
    string = re.sub(r"-+", "-", string)
    string = string.strip("-")
    return string
