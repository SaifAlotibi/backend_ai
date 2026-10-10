import time
from threading import Lock


class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 30,
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout

        self.failure_count = 0
        self.state = "CLOSED"
        self.last_failure_time = None

        self.lock = Lock()

    def allow_request(self) -> bool:
        with self.lock:

            # Normal operation
            if self.state == "CLOSED":
                return True

            # Service was failing, check recovery timeout
            if self.state == "OPEN":
                if (
                    self.last_failure_time is not None
                    and time.time() - self.last_failure_time
                    >= self.recovery_timeout
                ):
                    self.state = "HALF-OPEN"
                    return True

                return False

            # HALF-OPEN → allow one test request
            return True

    def record_success(self):
        with self.lock:
            self.failure_count = 0
            self.state = "CLOSED"
            self.last_failure_time = None

    def record_failure(self):
        with self.lock:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"

    def get_state(self):
        with self.lock:
            return self.state


circuit_breaker = CircuitBreaker(
    failure_threshold=5,
    recovery_timeout=30,
)