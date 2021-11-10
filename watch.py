from __future__ import annotations
from datetime import datetime
import json
import time
from typing import Optional

import notify2
import requests

from models import Success, Failure, History


class Watcher:
    def __init__(self, file_path: Optional[str] = None):
        if file_path is None:
            file_path = f"data/{datetime.now().isoformat()[:-7]}.json"
        self.file_path = file_path
        self.history = History()
        self.current_event = None

    def _notify(self, message: str):
        # We don't want to send a notification on startup
        if self.current_event is not None:
            print(datetime.now().isoformat(), message)
            notify2.Notification(message).show()

    def success(self):
        now = time.time()
        if type(self.current_event) is not Success:
            if self.current_event is not None:
                self._notify("Connectivity restored")
                self.current_event.end = now
            self.current_event = Success(start=now)
            self.history.successes.append(self.current_event)
        self.current_event.end = now
        self.history.save(self.file_path)

    def failure(self, error: str):
        now = time.time()
        if type(self.current_event) is not Failure or (
            self.current_event is not None and self.current_event.error != error
        ):
            if self.current_event is not None:
                self._notify(error)
                self.current_event.end = now
            self.current_event = Failure(error=error, start=now)
            self.history.failures.append(self.current_event)
        self.current_event.end = now
        self.history.save(self.file_path)


def main():
    notify2.init("Connectionator")
    watcher = Watcher()
    try:
        while True:
            try:
                requests.get("http://google.com", timeout=3)
                watcher.success()
            except requests.exceptions.RequestException as e:
                raw_error = repr(e)
                sanitized_error = raw_error.replace("0x[0-9a-f]+", "0x0000")
                watcher.failure(sanitized_error)
            time.sleep(5)
    except KeyboardInterrupt:
        # No need to throw exception traces, just exit silently
        pass


if __name__ == "__main__":
    main()
