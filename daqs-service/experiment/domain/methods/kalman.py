class ScalarKalmanFilter:
    """Filtr Kalmana dla pojedynczej, skalarnej wielkości"""

    def __init__(self, process_variance: float, measurement_variance: float, initial_estimate: float = 0.0):
        self._process_variance = process_variance
        self._measurement_variance = measurement_variance
        self._estimate = initial_estimate
        self._error_estimate = 1.0

    def update(self, measurement: float) -> float:
        # Predykcja
        self._error_estimate += self._process_variance

        kalman_gain = self._error_estimate / (self._error_estimate + self._measurement_variance)
        self._estimate += kalman_gain * (measurement - self._estimate)
        self._error_estimate *= (1 - kalman_gain)

        return self._estimate