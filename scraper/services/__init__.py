from scraper.services.mtgo import scrape_mtgo as mtgo
from scraper.services.mtgprime import get_qualified_players as mtgprime
from scraper.services.mtgtop8 import scrape_mtgtop8 as mtgtop8

__all__ = ["mtgo", "mtgtop8", "mtgprime"]
