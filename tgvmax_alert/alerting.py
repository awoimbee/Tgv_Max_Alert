from typing import List
from urllib import request, parse
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
import smtplib
import logging

logger = logging.getLogger(__name__)


class Alerting:
    ALERT_TYPES = ["SMS", "EMAIL"]

    def __init__(self, alert_types: List[str]):
        self.creds = json.load(open("./secret.json"))
        self.alert_types = set(alert_types)
        for a in alert_types:
            assert a in self.ALERT_TYPES

    def _send_sms(self, message):
        sms = "https://smsapi.free-mobile.fr/sendmsg"
        sms += f"?user={self.creds['SMS_free']['username']}"
        sms += f"&pass={self.creds['SMS_free']['password']}"
        sms += f"&msg={parse.quote(message)}"
        request.urlopen(sms)

    def _send_email(self, message):
        config = self.creds["email"]
        raw_fromaddr = config.get("fromaddr", config["username"])
        fromaddr = f"tgvmax-alert <{raw_fromaddr}>"
        toaddrs = config.get("toaddr", raw_fromaddr)
        subject = "TGV MAX ALERT"
        email = (
            f"From {fromaddr}\n"
            + f"To: {toaddrs}\n"
            + f"Subject: {subject}\n\n"
            + message
        )
        conn = smtplib.SMTP(config["host"])
        conn.starttls()
        conn.login(config["username"], config["password"])
        try:
            conn.sendmail(fromaddr, toaddrs, email.encode("utf8"))
        finally:
            conn.quit()

    def _build_ouisncf_url(self, train_data):
        "returns URL to train ticket on https://oui.sncf"
        departure = (
            train_data["date"].replace("-", "")
            + "-"
            + train_data["heure_depart"].replace(":", "").rjust(4, "0")
        )
        url = "https://www.oui.sncf/proposition/?nbpax=1&share=1&highlight=Y"
        url += f"&dest={train_data['destination_iata']}"
        url += f"&orig={train_data['origine_iata']}"
        url += f"&departure={departure}"
        url += f"&trainNumber_0={train_data['train_no']}"
        return url

    def alert(self, train_data):
        message = (
            f"Train disponible {train_data['date']} !\n"
            + f"Origine: {train_data['origine']}\n"
            + f"Destination: {train_data['destination']}\n"
            + f"Départ à: {train_data['heure_depart']}\n"
            + f"Arrivée à: {train_data['heure_arrivee']}\n"
            + f"-> {self._build_ouisncf_url(train_data)}\n"
        )
        print("\033[32m" + message + "\033[0m\n")
        if "SMS" in self.alert_types:
            self._send_sms(message)
        if "EMAIL" in self.alert_types:
            self._send_email(message)
