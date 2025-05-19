import time

from scraper import services
from scraper.utils import mtgtop8_utils


def count_files() -> int:
    try:
        return len(list(mtgtop8_utils.BASE_PATH.rglob("*.json")))
    except Exception:
        return 0


def main():
    nb_files_before = count_files()
    print(f"Initial number of tournaments: {nb_files_before}")

    nb_files = -1
    while nb_files < count_files():
        nb_files = count_files()
        services.mtgtop8()
        time.sleep(1)

    print(f"Scraped {count_files() - nb_files_before} tournaments.")


if __name__ == "__main__":
    main()
