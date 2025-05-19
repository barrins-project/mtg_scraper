import re
import time
from datetime import date, datetime
from typing import List, Mapping, Tuple

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
    decks: Mapping[int, Deck] = {}

    top8_decks = [
        get_deck_from_top8(deck_tag)
        for deck_tag in tournament_soup.select("div.S14 a[href^='?e=']")
    ]
    for deck_id, deck_obj in top8_decks:
        decks[deck_id] = deck_obj

    out_decks = [
        get_deck_out_top8(deck_tag)
        for deck_tag in tournament_soup.select("div.S14 input[type='radio']")
    ]
    for deck_id, deck_obj in out_decks:
        decks[deck_id] = deck_obj

    return list(decks.values())


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
    deck_id = 0
    player_name = "Unknown Player"
    result = 0

    id_match = re.search(r"d=(\d+)", str(deck_tag["href"]))
    if id_match:
        deck_id = int(id_match.group(1))
    else:
        deck_id = int(re.split("=", str(deck_tag["href"]))[2][:-2])

    parent_block = deck_tag.parent
    if not parent_block:
        raise ValueError("Parent block not found")
    else:
        parent_block = parent_block.parent
    if not parent_block:
        raise ValueError("Parent block not found")
    else:
        parent_block = parent_block.parent

    if parent_block:
        player_tag = parent_block.find("a", attrs={"class": "player"})
        if player_tag:
            player_name = player_tag.get_text(strip=True)

        for div_tag in parent_block.find_all("div"):
            div_text = div_tag.get_text(strip=True)
            if div_text:
                result_match = re.search(r"(\d(?:-\d)?)", div_text)
                if result_match:
                    result_text = result_match.group(1)
                    if "-" in result_text:
                        result = int(result_text.split("-")[0])
                    else:
                        result = int(result_text)

    mainboard, sideboard = get_decklist(deck_id)
    if not mainboard:
        raise ValueError("Mainboard not found")

    return (
        deck_id,
        Deck(
            date=datetime.now().date(),
            player=player_name,
            result=result,
            anchor_uri=f"https://mtgtop8.com/event{str(deck_tag["href"])}",
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
        cardentries.append(handle_line(line))

    return cardentries


def handle_line(line: str) -> CardEntry:
    parts = line.strip().split(" ", maxsplit=1)
    if len(parts) < 2:
        return CardEntry(name="Unknown Card", count=0)

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
