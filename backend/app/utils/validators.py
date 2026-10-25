from datetime import datetime, date
from typing import Optional, Tuple
from app.utils.datetime_utils import parse_utc_timestamp, UTC_TZ


def validate_date_string(date_str: Optional[str], field_name: str = "date") -> Optional[date]:
    """Validates that a string is in YYYY-MM-DD format."""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError(f"Invalid {field_name} format. Expected YYYY-MM-DD (e.g. 2026-01-15).")


def validate_date_range(
    start_date_str: Optional[str],
    end_date_str: Optional[str],
    default_start: str = "2026-01-01",
    default_end: str = "2026-01-31",
) -> Tuple[date, date]:
    """
    Validates and returns a (start_date, end_date) pair.
    Defaults to January 2026 if not specified.
    """
    start = validate_date_string(start_date_str, "start_date") or datetime.strptime(default_start, "%Y-%m-%d").date()
    end = validate_date_string(end_date_str, "end_date") or datetime.strptime(default_end, "%Y-%m-%d").date()

    if start > end:
        raise ValueError(f"start_date ({start}) cannot be after end_date ({end})")

    return start, end


def validate_pagination_params(
    page_str: Optional[str] = "1",
    per_page_str: Optional[str] = "50",
    max_per_page: int = 500,
) -> Tuple[int, int]:
    """Validates pagination page and per_page parameters."""
    try:
        page = int(page_str or 1)
        per_page = int(per_page_str or 50)
    except ValueError:
        raise ValueError("page and per_page must be positive integers")

    if page < 1:
        raise ValueError("page must be >= 1")
    if per_page < 1:
        raise ValueError("per_page must be >= 1")
    if per_page > max_per_page:
        per_page = max_per_page

    return page, per_page
