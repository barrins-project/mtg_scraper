from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from scraper.schemas.deck import Deck
    from scraper.schemas.round import Round
    from scraper.schemas.standing import Standing
    from scraper.schemas.tournament import Tournament


class MTGScrape(BaseModel):
    tournament: "Tournament"
    decks: list["Deck"] = []
    rounds: list["Round"] = []
    standings: list["Standing"] = []
