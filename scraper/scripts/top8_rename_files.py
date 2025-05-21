import json
import re
from typing import Mapping

from scraper.utils.mtgtop8 import BASE_PATH, sanitize_string


def rename_existing_files():
    for json_file in BASE_PATH.rglob("*.json"):
        try:
            with open(json_file, encoding="utf-8") as f:
                data = json.load(f)

            tournament: Mapping[str, str] = data.get("tournament", {})
            tid = re.search(r"event\?e=(\d+)", tournament.get("url", ""))
            if not tid:
                print(f"❌ Tournament ID not found in URL: {tournament.get('url')}")
                continue

            tournament_id = tid.group(1)
            tournament_format = sanitize_string(tournament.get("format", ""))
            tournament_name = sanitize_string(tournament.get("name", ""))

            new_name = f"{tournament_id}_{tournament_format}_{tournament_name}.json"
            new_path = json_file.parent / new_name

            if new_path != json_file:
                print(f"🔄 Renaming {json_file.name} -> {new_name}")
                json_file.rename(new_path)

        except Exception as e:
            print(f"⚠️ Error processing {json_file}: {e}")
            continue

    return


if __name__ == "__main__":
    rename_existing_files()
