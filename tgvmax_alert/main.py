#!/usr/bin/env python3

import argparse
import logging

import parsers
from alerting import Alerting
from check_availability import CheckAvailability

logger = logging.getLogger(__name__)


def parse_arguments():
    parser = argparse.ArgumentParser(description="TGV_Max_Alert")
    parser.add_argument(
        "--date",
        required=True,
        type=parsers.date,
        help="date format: YYYY-MM-DD",
    )
    parser.add_argument(
        "--time-range",
        type=parsers.time_range,
        required=True,
        help="hour format: 11:18. Monitor between 11h00 to 18h00",
    )
    parser.add_argument(
        "--origin",
        type=parsers.train_station,
        required=True,
        help="train origin station",
    )
    parser.add_argument(
        "--destination",
        type=parsers.train_station,
        required=True,
        help="train destination station",
    )
    parser.add_argument(
        "--alert", type=str, nargs="*", choices=Alerting.ALERT_TYPES, default=[]
    )
    parser.parse_args()
    args = parser.parse_args()
    return args


def main():
    args = vars(parse_arguments())
    CheckAvailability(**args).search()


if __name__ == "__main__":
    main()
