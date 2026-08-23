from dataclasses import dataclass, field

import discord

from FocoBot.timer import Timer


@dataclass(slots=True)
class PomodoroSession:
    timer: Timer = field(default_factory=Timer)
    round: int = 0
    phase: str = "aguardando"
    timer_message: discord.Message | None = None
    timer_color: int = 0
    starting: bool = False
