from enum import Enum


class TimerStatus(Enum):
    INITIALIZED = 1
    RUNNING = 2
    STOPPED = 3
    EXPIRED = 4
    PAUSED = 5


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

    def pause(self) -> bool:
        if self.status != TimerStatus.RUNNING:
            return False
        self.status = TimerStatus.PAUSED
        return True

    def resume(self) -> bool:
        if self.status != TimerStatus.PAUSED:
            return False
        self.status = TimerStatus.RUNNING
        return True

    def expire(self) -> bool:
        if not self.is_active():
            return False
        self.status = TimerStatus.EXPIRED
        return True

    def is_active(self) -> bool:
        return self.status in {TimerStatus.RUNNING, TimerStatus.PAUSED}

    def get_ticks(self) -> int:
        return self.ticks

    def convert_ticks(self) -> str:
        return self.format_ticks(self.ticks)

    def get_remaining_ticks(self) -> int:
        return max(0, self.max_ticks - self.ticks)

    def convert_remaining_ticks(self) -> str:
        return self.format_ticks(self.get_remaining_ticks())

    @staticmethod
    def format_ticks(ticks: int) -> str:
        minutes, seconds = divmod(ticks, 60)
        return f"{minutes:02d}:{seconds:02d}"

    def tick(self) -> None:
        if self.status != TimerStatus.RUNNING:
            return
        self.ticks += 1
        if self.ticks >= self.max_ticks:
            self.status = TimerStatus.EXPIRED
