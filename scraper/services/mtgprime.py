import pandas as pd
import requests
import json
from io import StringIO
from pathlib import Path
from scraper.parsers.mtgtop8 import HEADERS
from scraper.schemas import CircuitPlayer
from typing import List

BASE_PATH = Path(__file__).resolve().parent.parent.parent / "scraped" / "mtgprime.fr"
FILENAME = "2025_duel-commander_french-nationals_qualified_players.json"


def get_qualified_players() -> None:
    url = "https://mtgprime.fr/championnat-france-duel-commander-2025-qualifies/"
    qualified_players = get_tables_from_url(url)[0]

    players: List[CircuitPlayer] = []
    for _, row in qualified_players.iterrows():
        players.append(get_player_details(row))

    save_players_to_file(players)


def get_tables_from_url(url: str) -> List[pd.DataFrame]:
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()

    html_content = StringIO(response.text)
    tables = pd.read_html(html_content)
    return tables


def get_player_details(player_row: pd.Series) -> CircuitPlayer:
    surname = str(player_row["Nom"])
    name = str(player_row["Prénom"])
    pseudo = None
    if not surname or not name:
        surname, name, pseudo = None, None, surname or name

    is_regional_qualifier = "CR" in str(player_row["CR / Open"])
    is_open_qualifier = "Open" in str(player_row["CR / Open"])

    player = CircuitPlayer(
        **{
            "surname": surname,
            "name": name,
            "alias": pseudo,
            "is_challenger": "Challenger" in str(player_row["Type de Qualif"]),
            "is_invited": "Invité" in str(player_row["Type de Qualif"]),
            "region": str(player_row["Région"]),
            "tournament": str(player_row["Tournoi de Qualification"]),
            "is_regional_qualifier": is_regional_qualifier,
            "is_open_qualifier": is_open_qualifier,
            "is_other": not (is_regional_qualifier or is_open_qualifier),
        }
    )

    return player


def save_players_to_file(players: List[CircuitPlayer]) -> None:
    BASE_PATH.mkdir(parents=True, exist_ok=True)
    file_path = Path(BASE_PATH / FILENAME)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(
            [player.model_dump(mode="json") for player in players],
            f,
            ensure_ascii=False,
            indent=4,
        )

    print(f"📂 Data saved in {file_path}")
