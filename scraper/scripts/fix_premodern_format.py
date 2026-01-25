"""Ce script permet de corriger le format des scrapping Premodern.

Suite à la PR #1: https://github.com/barrins-project/mtg_scraper/pull/1
"""

import json
from pathlib import Path
from typing import List

BASE_PATH = Path(__file__).resolve().parent.parent.parent / "scraped"


def get_all_premodern_files() -> List[Path]:
    res: List[Path] = []
    for path in BASE_PATH.rglob("*.json"):
        if "premodern" in str(path):
            res.append(path)
    return res


def fix_format(file: Path) -> None:
    if not file.exists():
        return

    with open(file) as f:
        data = json.load(f)

    ori_format = data["tournament"]["format"]
    new_format = "Premodern" if ori_format == "Unknown Format" else ori_format
    data["tournament"]["format"] = new_format

    if ori_format != new_format:
        with open(file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)


def fix_premodern_format_name() -> None:
    for f in get_all_premodern_files():
        fix_format(f)


if __name__ == "__main__":
    fix_premodern_format_name()
