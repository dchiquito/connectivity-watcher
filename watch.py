from __future__ import annotations
from dataclasses import asdict, dataclass, field
from datetime import datetime
import json
import time
from typing import Optional

import notify2
import requests


@dataclass
class Success:
    start: float
    end: Optional[float] = None


@dataclass
class Failure:
    error: str
    start: float
    end: Optional[float] = None


@dataclass
class History:
    successes: list[Success] = field(default_factory=list)
    failures: list[Failure] = field(default_factory=list)
    current_event: Optional[Success | Failure] = None

    def _notify(self, message: str):
        # We don't want to send a notification on startup
        if self.current_event is not None:
            print(datetime.now().isoformat(), message)
            notify2.Notification(message).show()

    def success(self):
        if type(self.current_event) is not Success:
            self._notify("Connectivity restored")
            self.current_event = Success(start=time.time())
            self.successes.append(self.current_event)
        self.current_event.end = time.time()

    def failure(self, error: str):
        if type(self.current_event) is not Failure:
            self._notify(error)
            self.current_event = Failure(error=error, start=time.time())
            self.failures.append(self.current_event)
        self.current_event.end = time.time()

    @classmethod
    def load(name: str) -> History:
        with open(name, "r") as f:
            return History(**json.load(f))

    def save(self, name: str):
        with open(name, "w") as f:
            json.dump(asdict(self), f)


def main():
    notify2.init("Connectionator")
    file_name = f"data/{datetime.now().isoformat()[:-7]}.json"
    history = History()
    try:
        while True:
            try:
                requests.get("http://google.com", timeout=3)
                history.success()
            except requests.exceptions.ConnectTimeout:
                history.failure("ConnectTimeout")
            except requests.exceptions.ConnectionError:
                history.failure("ConnectionError")
            time.sleep(5)
    except KeyboardInterrupt:
        history.save(file_name)


if __name__ == "__main__":
    main()
