from datetime import date, datetime
from typing import List, Optional


def parse_date(
    date_text: object,
    formats: List[str] = ["%m/%d/%Y", "%B %d, %Y"],
) -> Optional[date]:
    try:
        if isinstance(date_text, date):
            return date_text
        if isinstance(date_text, datetime):
            return date_text.date()
        if isinstance(date_text, str):
            for fmt in formats:
                try:
                    return datetime.strptime(date_text.strip(), fmt).date()
                except ValueError:
                    continue
    except Exception as e:
        print(f"❌ Error parsing date from string: {e} // input={repr(date_text)}")
    return None


def get_month_range(date_from: datetime, date_to: datetime):
    date_tuples = []
    for year in range(date_from.year, date_to.year + 1):
        start_month = date_from.month if year == date_from.year else 1
        end_month = date_to.month if year == date_to.year else 12
        for month in range(start_month, end_month + 1):
            date_tuples.append((year, month))
    return date_tuples
