import numpy as np
from collections import deque

class StabilityDetector:
    def __init__(self, window_size: int = 10, threshold: float = 0.05):
        self._window: deque[float] = deque(maxlen=window_size)
        self._threshold = threshold

    def add_sample(self, value: float) -> None:
        self._window.append(value)

    def is_stable(self) -> bool:
        if len(self._window) < self._window.maxlen:
            return False

        x = np.array(len(self._window)) # Indeksy
        y = np.array(self._window) # Wartości

        slope, intercept = np.polyfit(x, y, deg=1)  # dopasowanie linii prostej: y = slope*x + intercept

        return abs(slope) < self._threshold

    def reset(self) -> None:
        self._window.clear()