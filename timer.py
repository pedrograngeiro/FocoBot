import asyncio
import discord
from enum import Enum
from discord.ext import commands


class TimerStatus(Enum):
    INICIALIZADO = 1
    RODANDO = 2
    PARADO = 3
    FINALIZADO = 4


class Timer:
    def __init__(self):
        self.status = TimerStatus.INICIALIZADO
        self.ticks = 0
        self.round = 0
        self.descanso = 0

    def get_status(self):
        return self.status

    def start(self, max_ticks):
        self.max_ticks = max_ticks
        self.status = TimerStatus.RODANDO
        self.ticks = 0

    def stop(self):
        self.status = TimerStatus.PARADO

    def get_ticks(self):
        return self.ticks

    def tick(self):
        self.ticks += 1
        if self.get_ticks() >= self.max_ticks:
            self.status = TimerStatus.FINALIZADO

    def get_round(self):
        return self.round, self.descanso

    def add_round(self):
        if self.get_status() == TimerStatus.RODANDO:
            self.round += 1
        if self.get_status() == TimerStatus.FINALIZADO:
            self.descanso += 1


