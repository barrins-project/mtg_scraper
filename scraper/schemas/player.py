from pydantic import BaseModel
from typing import Optional


class CircuitPlayer(BaseModel):
    surname: Optional[str] = None
    name: Optional[str] = None
    alias: Optional[str] = None
    is_qualified: bool = True
    is_challenger: bool = False
    is_invited: bool = False
    region: str
    tournament: str
    is_regional_qualifier: bool
    is_open_qualifier: bool
    is_other: bool

    model_config = {"from_attributes": True}
