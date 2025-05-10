from datetime import date
from typing import List, Optional

from pydantic import BaseModel


class Tournament(BaseModel):
    date: date
    name: str
    url: str
    format: str
    players: int = 0


class CardEntry(BaseModel):
    count: int
    name: str


class Deck(BaseModel):
    date: date
    player: str
    result: Optional[int] = None
    anchor_uri: str
    mainboard: List[CardEntry]
    sideboard: Optional[List[CardEntry]] = None


class Match(BaseModel):
    player_1: str
    player_2: str
    result: str


class Round(BaseModel):
    round_name: str
    matches: List[Match] = []


class Standing(BaseModel):
    rank: int
    player: str
    points: int
    wins: int
    losses: int
    draws: int
    omwp: float
    gwp: float
    ogwp: float


class Scrape(BaseModel):
    tournament: Tournament
    decks: List[Deck] = []
    rounds: List[Round] = []
    standings: List[Standing] = []
    
