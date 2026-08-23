import pytest

from FocoBot.config import PomodoroConfig


def test_default_config_matches_classic_pomodoro():
    config = PomodoroConfig()

    assert config.focus_minutes == 25
    assert config.short_break_minutes == 5
    assert config.long_break_minutes == 10
    assert config.rounds_before_long_break == 4
    assert config.focus_seconds == 1500
    assert config.short_break_seconds == 300
    assert config.long_break_seconds == 600


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("focus_minutes", 0),
        ("focus_minutes", 181),
        ("short_break_minutes", 61),
        ("long_break_minutes", 0),
        ("rounds_before_long_break", 13),
    ],
)
def test_config_rejects_values_outside_safe_limits(field, value):
    with pytest.raises(ValueError):
        PomodoroConfig(**{field: value})
