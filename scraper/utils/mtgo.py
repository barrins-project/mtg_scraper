import json
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from bs4 import BeautifulSoup
from selenium.webdriver.chrome.webdriver import WebDriver

from scraper.parsers import mtgo as parser
from scraper.schemas import MTGScrape

BASE_URL = "https://www.mtgo.com/decklists/"
BASE_PATH = Path(__file__).resolve().parent.parent.parent / "scraped" / "mtgo"


def we_should_scrape_it(tournament_url: str, max_days_to_be_recent: int = 2) -> bool:
    filename = sanitize_filename(tournament_url[30:]) + ".json"

    already_scraped = False
    recent_scrape = False
    for path in BASE_PATH.rglob(filename):
        if path.is_file():
            already_scraped = True
            match = re.search(r"(\d{4})-(\d{2})-(\d{2})", tournament_url)
            if match:
                year, month, day = map(int, match.groups())
                age = datetime.now() - datetime(year, month, day)
                recent_scrape = age.days < max_days_to_be_recent

    if already_scraped and not recent_scrape:
        print(f"⛔ Tournoi déjà scrappé (ancien) ignoré : {tournament_url}")
        return False

    return True


def sanitize_filename(name: str) -> str:
    name = name.lower()
    name = re.sub(r"[^a-z0-9]+", "-", name)
    name = re.sub(r"-+", "-", name)
    name = name.strip("-")
    return name


def scrape_tournament(
    driver: WebDriver, url: str, sleep_time: int = 5
) -> Optional[MTGScrape]:
    driver.get(url)
    time.sleep(sleep_time)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    tournament = parser.tournament(soup, url)
    if not tournament:
        print("❌ Element manquant dans les données du tournoi, extraction annulée.")
        return None

    return MTGScrape(
        tournament=tournament.model_dump(mode="json"),
        decks=[deck.model_dump(mode="json") for deck in parser.decks(soup, url)],
        rounds=[round.model_dump(mode="json") for round in parser.rounds(soup)],
        standings=[stding.model_dump(mode="json") for stding in parser.standings(soup)],
    )


def save_tournament_scrape(scrape: MTGScrape) -> None:
    tournament_url = scrape.tournament.url
    tournament_date = scrape.tournament.date

    # Parsing date to use it in dir path
    year = str(tournament_date.year)
    month = f"{tournament_date.month:02}"
    day = f"{(tournament_date.day):02}"

    # Making sure that YYYY/MM/DD folder exists
    dir_path = BASE_PATH / year / month / day
    dir_path.mkdir(parents=True, exist_ok=True)

    # Cleaning filename
    filename = sanitize_filename(tournament_url[30:]) + ".json"
    file_path = Path(dir_path / filename)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(scrape.model_dump(mode="json"), f, ensure_ascii=False, indent=4)

    print(f"📂 Data saved in {file_path}")
