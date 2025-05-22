import re
import time
from datetime import date, datetime
from typing import List, Mapping, Tuple, cast

import requests
from bs4 import BeautifulSoup, Tag

from scraper.schemas import FORMATS, CardEntry, Deck, Tournament

HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Max-Age": "3600",
    "User-Agent": (
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0)"
        + "Gecko/20100101 Firefox/52.0"
    ),
}


def get_tournament_soup(
    tournament_url: str, encoding: str = "iso-8859-1"
) -> BeautifulSoup:
    time.sleep(0.5)  # Avoid being blocked by the server
    req = requests.get(tournament_url, HEADERS, stream=True, timeout=5000)
    req.encoding = encoding
    return BeautifulSoup(req.content, "html.parser", from_encoding=encoding)


def tournament(tournament_url: str, tournament_soup: BeautifulSoup) -> Tournament:
    tournament_format = get_format(tournament_soup)
    if tournament_format == "Unknown Format":
        raise ValueError("Unknown format for tournament")

    return Tournament(
        date=get_date(tournament_soup),
        name=get_name(tournament_soup),
        url=tournament_url,
        format=tournament_format,
        players=get_players_qty(tournament_soup),
    )


def decks(tournament_soup: BeautifulSoup) -> List[Deck]:
    decks_dict: Mapping[int, Deck] = {}

    top8_tags = tournament_soup.select(
        ".chosen_tr div.S14 a[href^='?e='], .hover_tr div.S14 a[href^='?e=']"
    )
    out_tags = tournament_soup.select("div.S14 input[type='radio']")

    for deck_tag in top8_tags:
        deck_id, deck_obj = get_deck_from_top8(deck_tag)
        decks_dict[deck_id] = deck_obj

    for deck_tag in out_tags:
        deck_id, deck_obj = get_deck_out_top8(deck_tag)
        decks_dict[deck_id] = deck_obj

    return list(decks_dict.values())


def get_date(tournament_soup: BeautifulSoup) -> date:
    meta_arch = tournament_soup.find("div", class_="meta_arch")
    if meta_arch:
        parent = meta_arch.parent
        if parent:
            for tag in parent.find_all("div"):
                line = tag.get_text(strip=True)
                date_match = re.search(r"(\d{2}\/\d{2}\/\d{2})", line)
                if date_match:
                    day, month, year = date_match.group(1).split("/")
                    if int(year) + 2000 > datetime.now().year:
                        # Handle the case where the year is in the 1900s
                        year = str(int(year) - 100)
                    return datetime(int(year) + 2000, int(month), int(day)).date()

    # Default date if not found
    return datetime(1993, 8, 5).date()  # MTG first release


def get_name(tournament_soup: BeautifulSoup) -> str:
    event_title = tournament_soup.find("div", class_="event_title")
    if event_title:
        if "@" not in event_title.text:
            return event_title.get_text(strip=True)
        else:
            return event_title.get_text(strip=True).split("@")[0].strip()
    return ""


def get_format(tournament_soup: BeautifulSoup) -> str:
    meta_arch = tournament_soup.find("div", class_="meta_arch")
    if meta_arch:
        meta_arch_text = meta_arch.get_text(strip=True)
        for format_name in FORMATS:
            if format_name in meta_arch_text:
                return format_name

    return "Unknown Format"


def get_players_qty(tournament_soup: BeautifulSoup) -> int:
    meta_arch = tournament_soup.find("div", class_="meta_arch")
    if meta_arch:
        parent = meta_arch.parent
        if parent:
            for tag in parent.find_all("div"):
                line = tag.get_text(strip=True)
                if "players" in line.lower():
                    players_match = re.search(r"(\d+) players", line)
                    if players_match:
                        return int(players_match.group(1))

    return 0


def get_deck_from_top8(deck_tag: Tag) -> Tuple[int, Deck]:
    href = str(deck_tag.get("href", ""))
    id_match = re.search(r"d=(\d+)", href)
    if not id_match:
        raise ValueError(f"Deck ID not found in href: {href}")
    deck_id = int(id_match.group(1))

    player_name = "Unknown Player"
    result = 0
    parent_div = deck_tag.find_parent("div")
    container = cast(Tag, parent_div.find_parent("div")) if parent_div else None
    if not container:
        raise ValueError("Container block with player info not found.")

    player_tag = container.find("a", class_="player")
    if player_tag:
        player_name = player_tag.get_text(strip=True)

    # Cherche un score comme "1", "3-4", etc.
    for div in container.find_all("div"):
        text = div.get_text(strip=True)
        if re.fullmatch(r"\d+(-\d+)?", text):
            result = int(text.split("-")[0])
            break

    mainboard, sideboard = get_decklist(deck_id)
    if not mainboard:
        raise ValueError("Mainboard not found")

    return (
        deck_id,
        Deck(
            date=datetime.now().date(),
            player=player_name,
            result=result,
            anchor_uri=f"https://mtgtop8.com/event{href}",
            mainboard=mainboard,
            sideboard=sideboard,
        ),
    )


def get_deck_out_top8(deck_tag: Tag) -> Tuple[int, Deck]:
    deck_parent = deck_tag.parent
    if not deck_parent:
        raise ValueError("Parent block not found")

    deck_id = int(str(deck_tag["value"]))
    player_name = re.split(" - ", str(deck_tag.contents[0]), maxsplit=1)[1].strip()
    result = int(re.split("#", str(deck_parent["label"]), maxsplit=1)[1])

    mainboard, sideboard = get_decklist(deck_id)
    if not mainboard:
        raise ValueError("Mainboard not found")

    return (
        deck_id,
        Deck(
            date=datetime.now().date(),
            player=player_name,
            result=result,
            anchor_uri="",
            mainboard=mainboard,
            sideboard=sideboard,
        ),
    )


def get_decklist(deck_id: int) -> Tuple[List[CardEntry], List[CardEntry]]:
    # First call, sometimes necessary to force the server to return the decklist
    placebo_url = f"https://mtgtop8.com/event?e=1&d={deck_id}"
    get_tournament_soup(placebo_url)

    # Second call, this time we should get the decklist
    decklist_url = f"https://mtgtop8.com/mtgo?d={deck_id}"
    decklist_soup = str(get_tournament_soup(decklist_url).prettify())

    mainboard_soup = ""
    sideboard_soup = ""
    if "Sideboard" not in decklist_soup:
        mainboard_soup = decklist_soup
    else:
        mainboard_soup, sideboard_soup = decklist_soup.split("Sideboard")

    mainboard = get_cardentries(mainboard_soup)
    sideboard = get_cardentries(sideboard_soup)
    return mainboard, sideboard


def get_cardentries(decklist: str) -> List[CardEntry]:
    cardentries = []

    for line in decklist.split("\n"):
        line = line.strip()
        if len(line.split(" ", maxsplit=1)) == 2:
            cardentries.append(handle_line(line))

    return cardentries


def handle_line(line: str) -> CardEntry:
    parts = line.split(" ", maxsplit=1)
    qty = int(parts[0])
    name = sanitize_cardname(parts[1].strip())

    return CardEntry(name=name, count=qty)


def sanitize_cardname(card_name: str) -> str:
    # Remove Alchemy cards (starting with "A-")
    card_name = re.sub(r"^A-", "", card_name)
    # Remove error in text formatting
    card_name = card_name.replace("&amp;", "&")

    # May increase later

    return card_name
