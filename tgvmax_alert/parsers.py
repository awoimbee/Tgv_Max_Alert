from datetime import datetime
from argparse import ArgumentTypeError
import functools
from typing import List, Tuple
from urllib import request
from difflib import get_close_matches
import json
import datetime


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


def _parse_train_station(stations: List[str], in_station: str):
    stations_to_match = [s.upper()[: len(in_station)] for s in stations]
    try:
        match = get_close_matches(in_station.upper(), stations_to_match, 1)[0]
    except IndexError:
        raise ArgumentTypeError(
            f"Station '{in_station}' not found, available stations: {stations}"
        )
    return stations[stations_to_match.index(match)]


def _get_every_station():
    # TODO: cache this between restarts
    url = "https://ressources.data.sncf.com/api/v2/catalog/datasets/tgvmax/facets?facet=origine"
    resp = request.urlopen(url)
    data = json.loads(resp.read())
    return [facet["name"] for facet in data["facets"][0]["facets"]]


train_station = functools.partial(_parse_train_station, _get_every_station())
