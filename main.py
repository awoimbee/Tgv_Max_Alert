#!/usr/bin/env python3

from typing import Tuple
from urllib import request, parse
import json
import smtplib
import argparse
import datetime
import time


def parse_arguments():
    def parse_date(date: str) -> datetime.date:
        try:
            return datetime.datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            raise argparse.ArgumentTypeError(
                f"Incorrect date format, should be YYYY-MM-DD (got '{date}')"
            )

    def parse_time_range(time_range_str: str) -> Tuple[int, int]:
        hour_range = [int(h) for h in time_range_str.split(":", 1)]
        if (
            len(hour_range) == 2
            and 0 <= hour_range[0] <= 24
            and 0 <= hour_range[1] <= 24
        ):
            return hour_range
        raise argparse.ArgumentTypeError(
            f"Incorrect hour range (got '{time_range_str}')"
        )

    parser = argparse.ArgumentParser(description="TGV_Max_Alert")
    parser.add_argument(
        "--date",
        required=True,
        type=parse_date,
        help="date format: YYYY-MM-DD",
    )
    parser.add_argument(
        "--time-range",
        type=parse_time_range,
        required=True,
        help="hour format: 11:18. Monitor between 11h00 to 18h00",
    )
    parser.add_argument(
        "--origin", type=str, required=True, help="train origin station"
    )
    parser.add_argument(
        "--destination", type=str, required=True, help="train destination station"
    )
    parser.add_argument(
        "--alert", type=str, required=True, choices=["SMS", "EMAIL", "NO"]
    )
    parser.parse_args()
    args = parser.parse_args()
    return args


def prepare_url(args: argparse.Namespace) -> str:
    url = "https://ressources.data.sncf.com/api/records/1.0/search/?dataset=tgvmax&sort=date&facet=date&facet=origine&facet=destination"
    url += "&refine.origine=" + parse.quote(args.origin)
    url += "&refine.destination=" + parse.quote(args.destination)
    url += "&refine.date=" + parse.quote(str(args.date))
    return url


def send_sms(message):
    credential = json.load(open("./secret.json"))
    print(json.dumps(credential, indent=4))
    sms = "https://smsapi.free-mobile.fr/sendmsg?user="
    sms += credential["SMS"]["user"]
    sms += "&pass="
    sms += credential["SMS"]["password"]
    sms += "&msg="
    sms += message
    request.urlopen(sms)


def send_email(message):
    credential = json.load(open("./secret.json"))
    fromaddr = credential["EMAIL"]["my_email"]
    toaddrs = credential["EMAIL"]["toaddrs"]
    subject = "TGV MAX ALERT"
    msg = f"From {fromaddr}\nTo: {', '.join(toaddrs)}\nSubject: {subject}\n\n{message}"

    server = smtplib.SMTP("smtp.gmail.com:587")
    server.starttls()
    server.login(credential["EMAIL"]["my_email"], credential["EMAIL"]["my_password"])
    server.sendmail(fromaddr, toaddrs, msg)
    server.quit()


def send_alert(data, args):
    fields = data["fields"]
    message = (
        f"Train disponible {fields['date']} !\n"
        + f"Aller : {fields['origine']}\n"
        + f"Depart a : {fields['heure_depart']}\n"
        + f"Retour : {fields['destination']}\n"
        + f"Arrive a : {fields['heure_arrivee']}\n"
    )
    print("\033[32m" + message + "\033[0m\n")
    if args.alert == "SMS":
        send_sms(message)
    elif args.alert == "EMAIL":
        send_email(message)


def search_train(data: dict, args: argparse.Namespace) -> bool:
    alert = False
    nb_train = len(data["records"])
    for i in range(0, nb_train):
        if data["records"][i]["fields"]["od_happy_card"] == "OUI":
            hour = data["records"][i]["fields"]["heure_depart"]
            hourIn = int(hour.split(":", 1)[0])
            if args.time_range[0] <= hourIn <= args.time_range[1]:
                send_alert(data["records"][i], args)
                alert = True
    if alert == True:
        return True
    return False


def main():
    args = parse_arguments()
    url = prepare_url(args)
    while True:
        response = request.urlopen(url)
        data = json.loads(response.read())
        print(
            "Remaining requests before rate-limiting:",
            response.headers.get("X-RateLimit-Remaining"),
        )
        if search_train(data, args) == True:
            return 1
        else:
            print("Aucun train disponible ...")
        time.sleep(60)


if __name__ == "__main__":
    main()
