class Timer:
    def __init__(self):
        self.running = False
        self.ticks = 0
        self.max_ticks = 5  # 25 * 60

    def start(self):
        self.running = True
        self.ticks = 0

    def stop(self):
        self.running = False

    def is_running(self):
        return self.running

    def get_ticks(self):
        return self.ticks

    def tick(self):
        self.ticks += 1
