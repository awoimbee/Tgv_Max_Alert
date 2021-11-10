from datetime import datetime
from argparse import ArgumentTypeError
from typing import List, Tuple
from urllib import request
from difflib import get_close_matches
import json
import datetime

_EVERY_STATION = None


def date(date: str) -> datetime.date:
    try:
        return datetime.datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise ArgumentTypeError(
            f"Incorrect date format, should be YYYY-MM-DD (got '{date}')"
        )


def time_range(time_range_str: str) -> Tuple[int, int]:
    hour_range = [int(h) for h in time_range_str.split(":", 1)]
    if len(hour_range) == 2 and 0 <= hour_range[0] <= 24 and 0 <= hour_range[1] <= 24:
        return hour_range
    raise ArgumentTypeError(f"Incorrect hour range (got '{time_range_str}')")


def _get_every_station() -> List[str]:
    global _EVERY_STATION
    if _EVERY_STATION is None:
        url = "https://ressources.data.sncf.com/api/v2/catalog/datasets/tgvmax/facets?facet=origine"
        resp = request.urlopen(url)
        data = json.loads(resp.read())
        _EVERY_STATION = [facet["name"] for facet in data["facets"][0]["facets"]]
    return _EVERY_STATION


def train_station(station_name: str) -> str:
    every_station = _get_every_station()
    stations_to_match = [s.upper()[: len(station_name)] for s in every_station]
    try:
        match = get_close_matches(station_name.upper(), stations_to_match, 1)[0]
    except IndexError:
        raise ArgumentTypeError(
            f"Station '{station_name}' not found, available stations: {every_station}"
        )
    return every_station[stations_to_match.index(match)]
