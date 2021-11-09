from __future__ import annotations
from dataclasses import asdict, dataclass, field
from datetime import datetime
import json
import time

import notify2
import requests

@dataclass
class Success:
    time: float
    duration: float

@dataclass
class Failure:
    time: float
    error: str

@dataclass
class History:
    successes: list[Success] = field(default_factory=list)
    failures: list[Failure] = field(default_factory=list)

    def success(self, start: float, end: float):
        self.successes.append(Success(time=start, duration=end-start))

    def failure(self, start: float, error: str):
        self.failures.append(Failure(time=start, error=error))

def load_history(name: str) -> History:
    with open(name, 'r') as f:
        return History(**json.load(f))

def save_history(name: str, history: History):
    with open(name, 'w') as f:
        json.dump(asdict(history), f)

def main():
    notify2.init('Connectionator')
    file_name = datetime.now().isoformat()[:-7] + '.json'
    history = History()
    failing = False
    try:
        while True:
            start = time.time()
            try:
                requests.get('http://google.com', timeout=3)
            except requests.exceptions.ConnectTimeout:
                if not failing:
                    print(datetime.now().isoformat(),'ConnectTimeout')
                    notify2.Notification('ConnectTimeout', 'ConnectTimeout').show()
                    failing = True
                history.failure(start, 'ConnectTimeout')
            except requests.exceptions.ConnectionError:
                if not failing:
                    print(datetime.now().isoformat(),'ConnectionError')
                    notify2.Notification('ConnectionError', 'ConnectionError').show()
                    failing = True
                history.failure(start, 'ConnectionError')
            else:
                if failing:
                    print(datetime.now().isoformat(), 'Connection restored')
                    notify2.Notification('Connection restored', 'Connection restored').show()
                    failing = False
                end = time.time()
                history.success(start, end)
            time.sleep(5)
    except KeyboardInterrupt:
        print('done!')
        save_history(file_name, history)

if __name__ == '__main__':
    main()
