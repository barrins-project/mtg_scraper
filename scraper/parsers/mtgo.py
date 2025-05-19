import re
from datetime import date, timedelta
from typing import List, Optional

from bs4 import BeautifulSoup, Tag

from scraper.schemas import FORMATS, CardEntry, Deck, Match, Round, Standing, Tournament
from scraper.utils.date_parsing import parse_date
from scraper.utils.swiss_tournament import get_num_rounds


def tournament(soup: BeautifulSoup, tournament_url: str) -> Optional[Tournament]:
    tournament_date = get_date(soup)
    if not tournament_date:
        print("❌ Date manquante, extraction annulée.")
        return None

    return Tournament(
        date=tournament_date,
        name=get_name(soup),
        url=tournament_url,
        format=get_format(soup),
        players=get_player_qty(soup),
    )


def decks(soup: BeautifulSoup, tournament_url: str) -> List[Deck]:
    decks = []
    try:
        for deck in soup.select("section.decklist"):
            decks.append(get_deck(deck, tournament_url))
    except Exception as e:
        print("❌ Error with deck:", e)
    return decks


def rounds(soup: BeautifulSoup) -> List[Round]:
    return [get_round(round) for round in soup.select(".decklist-bracket-round")]


def standings(soup: BeautifulSoup) -> List[Standing]:
    standings_table = soup.select_one("#decklistStandings table.hidden-xs tbody")
    if not standings_table:
        return []

    nb_rounds = get_num_rounds(get_player_qty(soup))
    return [
        get_standing(row, nb_rounds)
        for row in standings_table.find_all("tr")
        if isinstance(row, Tag) and row.find_all("td")  # éviter les lignes vides
    ]


def get_date(soup: BeautifulSoup) -> Optional[date]:
    try:
        date_element = soup.select_one("p.decklist-posted-on")
        if not date_element:
            print("⚠️ Aucune balise contenant la date a été trouvée.")
            return None

        date_text = date_element.get_text(strip=True).replace("Posted on ", "")
        if not date_text:
            print("⚠️ Texte de date vide dans la balise.")
            return None

        parsed_date = parse_date(date_text)
        if parsed_date:
            return parsed_date - timedelta(days=1)
        else:
            print("⚠️ Échec du parsing de date.")
            return None
    except Exception as e:
        print(f"❌ Erreur inattendue dans get_date : {e}")


def get_name(soup: BeautifulSoup) -> str:
    title_element = soup.select_one("h1.decklist-title")
    return title_element.get_text(strip=True) if title_element else "Unknown Tournament"


def get_format(soup: BeautifulSoup) -> str:
    parsed_name = get_name(soup)
    for format_item in FORMATS:
        if format_item in parsed_name:
            return format_item
    return "Unknown Format"


def get_player_qty(soup: BeautifulSoup) -> int:
    players_element = soup.select_one("h2.decklist-player-count")
    if players_element:
        players_text = players_element.get_text(strip=True)
        match = re.search(r"(\d+)", players_text)
        return int(match.group(1)) if match else 0
    return 0


def get_deck(deck_section: Tag, url: str) -> Deck:
    player_tag = deck_section.find("p", class_="decklist-player")
    player_info = player_tag.get_text(strip=True) if player_tag else ""
    player_name, position_text = player_info.rsplit(" (", 1)

    try:
        position_number = int(position_text.split("Place")[0].strip()[:-2])
    except ValueError:
        position_number = None

    date_tag = deck_section.find("p", class_="decklist-date")
    event_date = parse_date(date_tag.get_text(strip=True) if date_tag else "08/05/1993")

    mainboard, sideboard = [], []
    mainboard_tag = deck_section.select(".decklist-sort-type .decklist-category")
    for type_tag in mainboard_tag:
        for card_tag in type_tag.select(".decklist-category-card"):
            card_line = card_tag.get_text(separator=" ", strip=True)
            match = re.match(r"(\d+)[xX]?\s+(.*)", card_line)
            if match:
                qty, name = int(match.group(1)), match.group(2)
                mainboard.append(CardEntry(name=name, count=qty))

    sideboard_tag = deck_section.select_one(".decklist-sideboard")
    if sideboard_tag:
        for card_tag in sideboard_tag.select(".decklist-category-card"):
            card_line = card_tag.get_text(separator=" ", strip=True)
            match = re.match(r"(\d+)[xX]?\s+(.*)", card_line)
            if match:
                qty, name = int(match.group(1)), match.group(2)
                sideboard.append(CardEntry(name=name, count=qty))

    return Deck(
        date=event_date,
        player=player_name,
        result=position_number,
        anchor_uri=f"{url}#{deck_section['id']}",
        mainboard=mainboard,
        sideboard=sideboard,
    )


def get_round(round_block: Tag) -> Round:
    round_name = round_block.select_one(".decklist-bracket-round-title")
    round_name = round_name.get_text(strip=True) if round_name else "Unknown Round"

    return Round(
        round_name=round_name,
        matches=[
            get_match(match_wrapper)
            for match_wrapper in round_block.select(".decklist-bracket-match-wrapper")
        ],
    )


def get_match(match_wrapper: Tag) -> Match:
    players = match_wrapper.select(".decklist-bracket-player")

    if len(players) == 2:
        winner_text = players[0].get_text(strip=True)
        loser_text = players[1].get_text(strip=True)
        if "  " in winner_text:
            winner_name, score = winner_text.split("  ", 1)
            winner_name = winner_name.strip()
            score = score.strip()
        else:
            winner_name = winner_text
            score = ""

        return Match(player_1=winner_name, player_2=loser_text, result=score)

    return Match(player_1="Unknown Player", player_2="Unknown Player", result="0-0-0")


def get_standing(row: Tag, nb_rounds: int) -> Standing:
    cols = row.find_all("td")
    if len(cols) != 6:
        raise ValueError("Invalid standing row")

    points = int(cols[2].get_text(strip=True))
    wins = points // 3
    draws = points % 3
    losses = nb_rounds - wins - draws

    return Standing(
        rank=int(cols[0].get_text(strip=True)),
        player=cols[1].get_text(strip=True),
        points=points,
        wins=wins,
        losses=losses,
        draws=draws,
        omwp=float(cols[3].get_text(strip=True).rstrip("%")) / 100,
        gwp=float(cols[4].get_text(strip=True).rstrip("%")) / 100,
        ogwp=float(cols[5].get_text(strip=True).rstrip("%")) / 100,
    )
