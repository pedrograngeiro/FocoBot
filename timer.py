
from enum import Enum

class TimerStatus(Enum):
    INITIALIZED = 1
    RUNNING = 2
    STOPPED = 3
    EXPIRED = 4

class Timer:
    def __init__(self):
        self.status = TimerStatus.INITIALIZED
        self.ticks = 0

    def get_status(self):
        return self.status


    def start(self, max_ticks):
        self.max_ticks = max_ticks
        self.status = TimerStatus.RUNNING
        self.ticks = 0

    def stop(self):
        self.status = TimerStatus.STOPPED

    def get_ticks(self):
        return self.ticks

    def tick(self):
        self.ticks += 1
        if self.get_ticks() >= self.max_ticks:
            self.status = TimerStatus.EXPIRED

