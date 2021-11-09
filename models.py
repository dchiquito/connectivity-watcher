from __future__ import annotations

from dataclasses import InitVar, asdict, dataclass, field
import json
from typing import Optional


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

    @classmethod
    def load(file_path: str) -> History:
        with open(file_path, "r") as f:
            return History(**json.load(f))

    def save(self, file_path: str):
        with open(file_path, "w") as f:
            json.dump(asdict(self), f)
