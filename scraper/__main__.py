import argparse
from datetime import datetime, timedelta

from scraper import services


def main() -> None:
    today = datetime.now().strftime("%Y-%m")
    five_days_ago = (datetime.now() - timedelta(days=5)).strftime("%Y-%m")

    parser = argparse.ArgumentParser(
        prog="Barrin's Project - MTG Scrapper",
        description="CLI module to extract MTG tournaments from different sources",
        epilog="written by Spigushe, 2025",
    )

    parser.add_argument(
        "--source",
        choices=["mtgo", "mtgtop8", "mtgprime"],
        type=str,
        help="Source being scrapped (default: MTGO)",
        default="mtgo",
    )
    parser.add_argument(
        "--date-from",
        type=str,
        help="Date de début (format YYYY-MM)",
        default=five_days_ago,
    )
    parser.add_argument(
        "--date-to",
        type=str,
        help="Date de fin (format YYYY-MM)",
        default=today,
    )
    parser.add_argument(
        "--span",
        type=int,
        help="Nombre de tournois à inspecter",
        default=1000,
    )

    args = parser.parse_args()

    try:
        date_from = datetime.strptime(args.date_from, "%Y-%m")
        date_to = datetime.strptime(args.date_to, "%Y-%m")
    except ValueError:
        print("Erreur : le format des dates doit être YYYY-MM, ex: 2022-01")
        return

    if args.source == "mtgo":
        services.mtgo(date_from, date_to)
    if args.source == "mtgtop8":
        services.mtgtop8(args.span)
    if args.source == "mtgprime":
        services.mtgprime()


if __name__ == "__main__":
    main()
