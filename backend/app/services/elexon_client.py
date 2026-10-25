import time
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from app.utils.logger import get_logger
from app.utils.datetime_utils import format_utc_iso, parse_utc_timestamp

logger = get_logger("elexon_client")


class ElexonAPIError(Exception):
    """Custom exception raised when an Elexon BMRS API request fails."""
    pass


class ElexonClient:
    """
    Client for interacting with the official Elexon BMRS API.
    Supports resilient batch streaming for FUELHH and WINDFOR datasets.
    """

    def __init__(
        self,
        base_url: str = "https://data.elexon.co.uk/bmrs/api/v1",
        timeout: int = 30,
        max_retries: int = 3,
        backoff_factor: float = 1.5,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "UK-Wind-Power-Forecast-Intelligence/1.0",
            "Accept": "application/json",
        })

    def _get_with_retry(self, endpoint: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Executes GET request with bounded retries and exponential backoff."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        attempt = 0
        last_error = None

        while attempt < self.max_retries:
            attempt += 1
            try:
                logger.info(f"Elexon API Request (attempt {attempt}/{self.max_retries}): {endpoint} params={params}")
                response = self.session.get(url, params=params, timeout=self.timeout)

                if response.status_code == 200:
                    data = response.json()
                    # If endpoint returned a dict with 'data' key or direct list
                    if isinstance(data, dict) and "data" in data:
                        return data["data"]
                    elif isinstance(data, list):
                        return data
                    else:
                        logger.warning(f"Unexpected JSON structure from {endpoint}: {type(data)}")
                        return []
                elif response.status_code in (429, 500, 502, 503, 504):
                    logger.warning(
                        f"Elexon API returned status {response.status_code} for {endpoint}. Retrying..."
                    )
                    time.sleep(self.backoff_factor ** attempt)
                else:
                    raise ElexonAPIError(
                        f"Elexon API error {response.status_code} on {endpoint}: {response.text[:200]}"
                    )
            except (requests.RequestException, ValueError) as err:
                last_error = err
                logger.warning(f"Elexon API connection error (attempt {attempt}): {err}")
                if attempt < self.max_retries:
                    time.sleep(self.backoff_factor ** attempt)

        raise ElexonAPIError(
            f"Failed to fetch data from {endpoint} after {self.max_retries} attempts: {last_error}"
        )

    def fetch_actual_generation(
        self,
        settlement_date_from: date,
        settlement_date_to: date,
        fuel_type: str = "WIND",
    ) -> List[Dict[str, Any]]:
        """
        Fetches actual generation records from FUELHH/stream dataset.
        Filters for specific fuelType (default: WIND).
        
        Returns parsed list of records:
        [
            {
                "start_time_utc": datetime,
                "fuel_type": str,
                "generation_mw": float,
                "settlement_date": str,
                "settlement_period": int,
            }, ...
        ]
        """
        endpoint = "datasets/FUELHH/stream"
        params = {
            "settlementDateFrom": settlement_date_from.strftime("%Y-%m-%d"),
            "settlementDateTo": settlement_date_to.strftime("%Y-%m-%d"),
        }

        raw_records = self._get_with_retry(endpoint, params)
        validated_records = []

        for item in raw_records:
            if not isinstance(item, dict):
                continue
            item_fuel = item.get("fuelType")
            if fuel_type and item_fuel != fuel_type:
                continue

            try:
                start_time_str = item.get("startTime")
                generation_val = item.get("generation")
                if not start_time_str or generation_val is None:
                    continue

                start_dt = parse_utc_timestamp(start_time_str)
                gen_mw = float(generation_val)

                validated_records.append({
                    "start_time_utc": start_dt,
                    "fuel_type": item_fuel,
                    "generation_mw": gen_mw,
                    "settlement_date": item.get("settlementDate"),
                    "settlement_period": item.get("settlementPeriod"),
                })
            except (ValueError, TypeError) as err:
                logger.warning(f"Skipping malformed FUELHH record {item}: {err}")
                continue

        logger.info(
            f"Fetched {len(validated_records)} {fuel_type} actual generation records for "
            f"{settlement_date_from} to {settlement_date_to}"
        )
        return validated_records

    def fetch_wind_forecasts(
        self,
        publish_from_utc: datetime,
        publish_to_utc: datetime,
    ) -> List[Dict[str, Any]]:
        """
        Fetches wind generation forecasts from WINDFOR/stream dataset
        by publishDateTime window.
        
        Returns parsed list of records:
        [
            {
                "start_time_utc": datetime,
                "publish_time_utc": datetime,
                "generation_mw": float,
            }, ...
        ]
        """
        endpoint = "datasets/WINDFOR/stream"
        params = {
            "publishDateTimeFrom": format_utc_iso(publish_from_utc),
            "publishDateTimeTo": format_utc_iso(publish_to_utc),
        }

        raw_records = self._get_with_retry(endpoint, params)
        validated_records = []

        for item in raw_records:
            if not isinstance(item, dict):
                continue

            try:
                start_time_str = item.get("startTime")
                publish_time_str = item.get("publishTime")
                generation_val = item.get("generation")

                if not start_time_str or not publish_time_str or generation_val is None:
                    continue

                start_dt = parse_utc_timestamp(start_time_str)
                publish_dt = parse_utc_timestamp(publish_time_str)
                gen_mw = float(generation_val)

                validated_records.append({
                    "start_time_utc": start_dt,
                    "publish_time_utc": publish_dt,
                    "generation_mw": gen_mw,
                })
            except (ValueError, TypeError) as err:
                logger.warning(f"Skipping malformed WINDFOR record {item}: {err}")
                continue

        logger.info(
            f"Fetched {len(validated_records)} WINDFOR forecast records published between "
            f"{params['publishDateTimeFrom']} and {params['publishDateTimeTo']}"
        )
        return validated_records
