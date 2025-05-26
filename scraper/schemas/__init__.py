from scraper.schemas.deck import CardEntry, Deck
from scraper.schemas.player import CircuitPlayer
from scraper.schemas.round import Match, Round
from scraper.schemas.scraped_object import MTGScrape
from scraper.schemas.standing import Standing
from scraper.schemas.tournament import Tournament

TYPE_NAMESPACE = {
    "CardEntry": CardEntry,
    "Deck": Deck,
    "Match": Match,
    "MTGScrape": MTGScrape,
    "Round": Round,
    "Standing": Standing,
    "Tournament": Tournament,
}

MTGScrape.model_rebuild(_types_namespace=TYPE_NAMESPACE)


from scraper.schemas.formats import FORMATS as FORMATS

__all__ = [
    "CardEntry",
    "CircuitPlayer",
    "Deck",
    "Match",
    "MTGScrape",
    "Round",
    "Standing",
    "Tournament",
]
