from typing import TYPE_CHECKING, List

from pydantic import BaseModel

if TYPE_CHECKING:
    from scraper.schemas.deck import Deck
    from scraper.schemas.round import Round
    from scraper.schemas.standing import Standing
    from scraper.schemas.tournament import Tournament


class MTGScrape(BaseModel):
    tournament: "Tournament"
    decks: List["Deck"] = []
    rounds: List["Round"] = []
    standings: List["Standing"] = []
