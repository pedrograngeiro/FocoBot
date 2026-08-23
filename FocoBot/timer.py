from enum import Enum


class TimerStatus(Enum):
    INITIALIZED = 1
    RUNNING = 2
    STOPPED = 3
    EXPIRED = 4


class Timer:
    def __init__(self) -> None:
        self.status = TimerStatus.INITIALIZED
        self.ticks = 0
        self.max_ticks = 0

    def get_status(self) -> TimerStatus:
        return self.status

    def start(self, max_ticks: int) -> None:
        if max_ticks < 0:
            raise ValueError("max_ticks não pode ser negativo")
        self.max_ticks = max_ticks
        self.status = TimerStatus.RUNNING
        self.ticks = 0

    def stop(self) -> None:
        self.status = TimerStatus.STOPPED

    def get_ticks(self) -> int:
        return self.ticks

    def convert_ticks(self) -> str:
        minutes, seconds = divmod(self.ticks, 60)
        return f"{minutes:02d}:{seconds:02d}"

    def tick(self) -> None:
        if self.status != TimerStatus.RUNNING:
            return
        self.ticks += 1
        if self.ticks >= self.max_ticks:
            self.status = TimerStatus.EXPIRED
