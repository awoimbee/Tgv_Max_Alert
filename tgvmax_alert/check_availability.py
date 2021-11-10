from typing import List, Tuple, Union
from urllib import request, parse
from urllib.error import URLError
from datetime import date
import json
import logging
import time

from alerting import Alerting

logger = logging.getLogger(__name__)


class CheckAvailability:
    SLEEP_TIME = 10

    def __init__(
        self,
        alert: Union[Alerting, List[str]],
        date: date,
        time_range: Tuple[int, int],
        origin: str,
        destination: str,
        **kwargs,
    ):
        logger.info(
            f"Will search for a train from {origin} to {destination} the {date} between {time_range}..."
        )
        if type(alert) == list:
            alert = Alerting(alert)
        self.alerting = alert
        self.time_range = time_range
        self.origin = origin
        self.destination = destination
        self.date = date
        self.url = self._prepare_url()

        # Trains we already sent an alert for
        self.already_found = set()

    def _search_train(self, data: dict) -> bool:
        found = False
        for record in data["records"]:
            train_data = record["record"]["fields"]
            train_no = train_data["train_no"]
            if train_data["od_happy_card"] != "OUI":
                if train_no in self.already_found:
                    print(f"Train {train_no} not available anymore :(")  # TODO
                    del self.already_found[train_no]
                continue
            if train_no in self.already_found:
                continue
            departure = train_data["heure_depart"]
            hour = int(departure.split(":", 1)[0])
            if self.time_range[0] <= hour <= self.time_range[1]:
                self.already_found.add(train_no)
                self.alerting.alert(train_data)
                found = True
        return found

    def _prepare_url(self) -> str:
        url = "https://ressources.data.sncf.com/api/v2/catalog/datasets/tgvmax/records?order_by=date&facet=date&facet=origine&facet=destination"
        url += f"&refine=origine:{parse.quote(self.origin)}"
        url += f"&refine=destination:{parse.quote(self.destination)}"
        url += f"&refine=date:{parse.quote(str(self.date))}"
        return url

    def search(self):
        print(
            f"Searching for a train from {self.origin} to {self.destination} the {self.date} between {self.time_range}"
        )
        while True:
            try:
                response = request.urlopen(self.url)
                data = json.loads(response.read())
                self._search_train(data)
            except (URLError) as e:
                logger.error(f"ERROR: {e}, retrying in {self.SLEEP_TIME}s")
            time.sleep(self.SLEEP_TIME)
