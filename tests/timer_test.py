from timer import Timer, TimerStatus

def test_init_initializes_vars_properly():
    timer = Timer(max_ticks = 1)
    assert timer.get_status() == TimerStatus.INITIALIZED

    assert timer.get_ticks() == 0


def test_start_initializes_vars_properly():
    timer = Timer()
    timer.start()
    assert timer.get_status() == TimerStatus.RUNNING
    assert timer.get_ticks() == 0


def test_tick_increases_ticks():
    timer = Timer(max_ticks=2)
    timer.start()
    timer.tick()
    assert timer.get_status() == TimerStatus.RUNNING
    assert timer.get_ticks() == 1

def test_tick_will_expire_when_it_reaches_max_ticks():
    timer = Timer(max_ticks=2)
    timer.start()
    timer.tick()
    assert timer.get_status() == TimerStatus.RUNNING
    assert timer.get_ticks() == 1
    timer.tick()
    assert timer.get_status() == TimerStatus.EXPIRED
    assert timer.get_ticks() == 2