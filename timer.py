from enum import Enum

class TimerStatus(Enum):
    INICIALIZADO = 1
    RODANDO = 2
    PARADO = 3
    FINALIZADO = 4

class Timer:
    def __init__(self):
        self.status = TimerStatus.INICIALIZADO
        self.ticks = 0

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

