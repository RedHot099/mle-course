"""Reference solutions of the exercises in lecture 03."""

SOLUTIONS = {
    "e1": """
from dataclasses import dataclass
@dataclass(frozen=True)
class Window:
    start: int
    length: int
    def __post_init__(self):
        if self.length < 1:
            raise ValueError('length')
    @property
    def end(self):
        return self.start + self.length
    def overlaps(self, other):
        return self.start < other.end and other.start < self.end
""",
    "e2": """
from abc import ABC, abstractmethod
from statistics import median
class LocalForecaster(ABC):
    def __init__(self):
        self._history = None
    def fit(self, history):
        if not history:
            raise ValueError('empty')
        self._history = list(history)
        return self
    def predict(self, horizon):
        if self._history is None:
            raise RuntimeError('fit')
        return self._forecast(self._history, horizon)
    @abstractmethod
    def _forecast(self, history, horizon): ...
class MedianForecaster(LocalForecaster):
    def _forecast(self, history, horizon):
        return [median(history)] * horizon
""",
}
