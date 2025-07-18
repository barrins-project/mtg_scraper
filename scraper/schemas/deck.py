from datetime import date
from typing import List, Optional

from pydantic import BaseModel


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
    notes: Optional[str] = None
