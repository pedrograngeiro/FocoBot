import pytest

from FocoBot.timer import Timer, TimerStatus


def test_init_initializes_vars_properly():
    timer = Timer()
    assert timer.get_status() == TimerStatus.INITIALIZED
    assert timer.get_ticks() == 0


def test_start_initializes_vars_properly():
    timer = Timer()
    timer.start(max_ticks=2)
    assert timer.get_status() == TimerStatus.RUNNING
    assert timer.get_ticks() == 0


def test_tick_increases_ticks():
    timer = Timer()
    timer.start(max_ticks=2)
    timer.tick()
    assert timer.get_status() == TimerStatus.RUNNING
    assert timer.get_ticks() == 1


def test_tick_will_expire_when_it_reaches_max_ticks():
    timer = Timer()
    timer.start(max_ticks=2)
    timer.tick()
    assert timer.get_status() == TimerStatus.RUNNING
    assert timer.get_ticks() == 1
    timer.tick()
    assert timer.get_status() == TimerStatus.EXPIRED
    assert timer.get_ticks() == 2


def test_tick_does_nothing_while_stopped():
    timer = Timer()
    timer.start(max_ticks=2)
    timer.stop()
    timer.tick()
    assert timer.get_ticks() == 0


def test_convert_ticks_formats_elapsed_time():
    timer = Timer()
    timer.start(max_ticks=61)
    for _ in range(61):
        timer.tick()
    assert timer.convert_ticks() == "01:01"


def test_start_rejects_negative_duration():
    with pytest.raises(ValueError, match="negativo"):
        Timer().start(max_ticks=-1)


def test_pause_freezes_ticks_until_resume():
    timer = Timer()
    timer.start(max_ticks=3)
    timer.tick()

    assert timer.pause() is True
    timer.tick()
    assert timer.get_ticks() == 1
    assert timer.get_status() == TimerStatus.PAUSED

    assert timer.resume() is True
    timer.tick()
    assert timer.get_ticks() == 2
    assert timer.get_status() == TimerStatus.RUNNING


def test_expire_skips_running_or_paused_timer():
    timer = Timer()
    timer.start(max_ticks=10)
    timer.pause()

    assert timer.expire() is True
    assert timer.get_status() == TimerStatus.EXPIRED
    assert timer.expire() is False


def test_remaining_ticks_never_becomes_negative():
    timer = Timer()
    timer.start(max_ticks=1)
    timer.tick()
    timer.tick()

    assert timer.get_remaining_ticks() == 0
    assert timer.convert_remaining_ticks() == "00:00"
