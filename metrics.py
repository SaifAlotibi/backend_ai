import time
from threading import Lock


class Metrics:

    def __init__(self):
        self.lock = Lock()

        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.timeouts = 0

        self.total_latency = 0.0

    def request_started(self):
        with self.lock:
            self.total_requests += 1

    def request_completed(self, latency: float):
        with self.lock:
            self.successful_requests += 1
            self.total_latency += latency

    def request_failed(self, latency: float):
        with self.lock:
            self.failed_requests += 1
            self.total_latency += latency

    def request_timeout(self, latency: float):
        with self.lock:
            self.timeouts += 1
            self.failed_requests += 1
            self.total_latency += latency

    def get_metrics(self):

        with self.lock:

            completed = (
                self.successful_requests
                + self.failed_requests
            )

            if completed > 0:
                average_latency = (
                    self.total_latency / completed
                )
            else:
                average_latency = 0.0

            return {
                "total_requests": self.total_requests,
                "successful_requests": self.successful_requests,
                "failed_requests": self.failed_requests,
                "timeouts": self.timeouts,
                "average_latency": round(
                    average_latency,
                    3
                ),
            }


metrics = Metrics()