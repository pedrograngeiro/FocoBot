from timer import Timer


def test_start_initializes_vars_properly():
    timer = Timer()
    timer.start()
    assert timer.is_running()
    assert timer.get_ticks() == 0


def test_init_initializes_vars_properly():
    timer = Timer()
    assert not timer.is_running()
    assert timer.get_ticks() == 0

def test_tick_increases_ticks():
    timer = Timer()
    timer.start()
    timer.tick()
    assert timer.is_running()
    assert timer.get_ticks() == 1