from __future__ import annotations

from typing import Any, Dict, Union, get_args, get_origin

from pydantic import BaseModel


class CircuitPlayer(BaseModel):
    surname: str = ""
    name: str = ""
    alias: str = ""
    is_qualified: bool = True
    is_challenger: bool = False
    is_invited: bool = False
    region: str = ""
    tournament: str = ""
    is_regional_qualifier: bool = False
    is_open_qualifier: bool = False
    is_other: bool = False

    model_config = {"from_attributes": True}

    @classmethod
    def from_raw(cls, raw: Dict[str, Any]) -> CircuitPlayer:
        data: Dict[str, Any] = {}

        for name, field in cls.model_fields.items():
            v = raw.get(name, None)
            if v is None:
                continue

            expected = field.annotation
            origin = get_origin(expected)
            if origin is Union:
                args = tuple(a for a in get_args(expected) if a is not type(None))
                if len(args) == 1:
                    expected = args[0]

            if expected is str:
                data[name] = str(v)
            elif expected is bool:
                data[name] = bool(v)
            else:
                data[name] = v

        return cls(**data)
