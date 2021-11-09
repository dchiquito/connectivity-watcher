from __future__ import annotations
from datetime import datetime
import os

from models import Success, Failure, History


def load_data() -> list[History]:
    return [History.load(f"data/{file_name}") for file_name in os.listdir("data")]


def main():
    histories = load_data()
    for history in histories:
        for failure in history.failures:
            print(
                datetime.fromtimestamp(failure.start),
                failure.error,
                failure.end - failure.start,
            )


if __name__ == "__main__":
    main()
