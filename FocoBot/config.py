from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PomodoroConfig:
    focus_minutes: int = 25
    short_break_minutes: int = 5
    long_break_minutes: int = 10
    rounds_before_long_break: int = 4

    def __post_init__(self) -> None:
        limits = (
            ("foco", self.focus_minutes, 1, 180),
            ("pausa", self.short_break_minutes, 1, 60),
            ("pausa longa", self.long_break_minutes, 1, 60),
            ("ciclos", self.rounds_before_long_break, 1, 12),
        )
        for name, value, minimum, maximum in limits:
            if not minimum <= value <= maximum:
                raise ValueError(f"{name} deve estar entre {minimum} e {maximum}")

    @property
    def focus_seconds(self) -> int:
        return self.focus_minutes * 60

    @property
    def short_break_seconds(self) -> int:
        return self.short_break_minutes * 60

    @property
    def long_break_seconds(self) -> int:
        return self.long_break_minutes * 60
