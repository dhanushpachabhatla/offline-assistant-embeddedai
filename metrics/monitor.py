import psutil
import time
import os


class MetricsMonitor:

    def __init__(self):

        self.process = psutil.Process(os.getpid())

    def start_timer(self):

        self.start_time = time.time()

    def stop_timer(self):

        latency = time.time() - self.start_time
        return latency

    def memory_usage(self):

        return self.process.memory_info().rss / (1024 * 1024)

    def cpu_usage(self):

        return psutil.cpu_percent(interval=0.1)