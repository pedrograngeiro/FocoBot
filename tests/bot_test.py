import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

from FocoBot.__main__ import create_bot
from FocoBot.discord_cog import (
    COLOR_SUCCESS,
    SOUNDS,
    DiscordCog,
    make_progress_bar,
)
from FocoBot.timer import TimerStatus


def test_bot_uses_required_intents_and_preserves_prefix():
    bot = create_bot()

    assert bot.command_prefix == "!"
    assert bot.intents.message_content is True


def test_setup_hook_registers_legacy_commands():
    bot = create_bot()
    bot.tree.sync = AsyncMock()

    asyncio.run(bot.setup_hook())

    assert {command.name for command in bot.commands} == {
        "ajuda",
        "comecar",
        "configuracao",
        "configurar",
        "encerrar",
        "parar",
        "pausar",
        "pular",
        "retomar",
        "tempo",
    }
    assert bot.get_command("começar").name == "comecar"
    assert bot.get_command("foco").name == "comecar"
    assert bot.get_command("config").name == "configuracao"
    assert bot.get_command("tempos").name == "configuracao"
    bot.tree.sync.assert_awaited_once_with()


def test_hybrid_commands_expose_application_commands():
    bot = create_bot()
    bot.tree.sync = AsyncMock()

    asyncio.run(bot.setup_hook())

    assert {command.name for command in bot.tree.get_commands()} == {
        "ajuda",
        "comecar",
        "configuracao",
        "configurar",
        "encerrar",
        "parar",
        "pausar",
        "pular",
        "retomar",
        "tempo",
    }


def test_audio_assets_are_resolved_from_the_project():
    assert all(path.is_file() for path in SOUNDS.values())


def test_progress_bar_handles_empty_partial_and_complete_states():
    assert make_progress_bar(0, 100, length=10) == "░" * 10
    assert make_progress_bar(50, 100, length=10) == "█" * 5 + "░" * 5
    assert make_progress_bar(100, 100, length=10) == "█" * 10


def test_timer_embed_exposes_live_progress():
    cog = DiscordCog(create_bot())
    session = cog.get_session(1)
    session.round = 2
    session.phase = "foco"
    session.timer_color = COLOR_SUCCESS
    session.timer.start(max_ticks=10)
    for _ in range(4):
        session.timer.tick()

    embed = cog.build_timer_embed(session).to_dict()

    assert embed["title"].endswith("Foco")
    assert embed["description"] == "`████░░░░░░░░`"
    assert embed["fields"] == [
        {"inline": True, "name": "Restante", "value": "00:06"},
        {"inline": True, "name": "Decorrido", "value": "00:04"},
        {"inline": True, "name": "Status", "value": "Rodando"},
    ]
    assert embed["footer"]["text"].startswith("Round 2")

    session.timer.tick()
    assert cog.build_timer_embed(session).title.startswith("◓")


def test_paused_timer_embed_uses_static_indicator():
    cog = DiscordCog(create_bot())
    session = cog.get_session(1)
    session.phase = "pausa curta"
    session.timer.start(max_ticks=10)
    session.timer.pause()

    embed = cog.build_timer_embed(session).to_dict()

    assert embed["title"] == "⏸ Pausa Curta"
    assert embed["fields"][2]["value"] == "Pausado"


def test_refresh_timer_message_edits_the_existing_message():
    cog = DiscordCog(create_bot())
    session = cog.get_session(1)
    original_message = AsyncMock()
    updated_message = AsyncMock()
    original_message.edit = AsyncMock(return_value=updated_message)
    session.timer_message = original_message

    asyncio.run(cog.refresh_timer_message(session))

    original_message.edit.assert_awaited_once()
    assert session.timer_message is updated_message


def test_configurations_are_isolated_by_guild():
    cog = DiscordCog(create_bot())

    first = cog.get_config(1)
    second = cog.get_config(2)

    assert first is not second
    assert first == second


def test_timer_sessions_are_isolated_by_guild():
    cog = DiscordCog(create_bot())
    first = cog.get_session(1)
    second = cog.get_session(2)

    first.timer.start(max_ticks=10)
    second.timer.start(max_ticks=20)
    first.timer.tick()
    second.timer.pause()

    assert first is not second
    assert first.timer.get_ticks() == 1
    assert first.timer.get_status() == TimerStatus.RUNNING
    assert second.timer.get_ticks() == 0
    assert second.timer.get_status() == TimerStatus.PAUSED


def test_stopping_one_guild_does_not_stop_another():
    cog = DiscordCog(create_bot())
    cog.show_message = AsyncMock()
    cog.refresh_timer_message = AsyncMock()
    first = cog.get_session(1)
    second = cog.get_session(2)
    first.timer.start(max_ticks=10)
    second.timer.start(max_ticks=10)
    ctx = AsyncMock()
    ctx.guild = SimpleNamespace(id=1)
    ctx.voice_client = None

    asyncio.run(cog.stop.callback(cog, ctx))

    assert first.timer.get_status() == TimerStatus.STOPPED
    assert second.timer.get_status() == TimerStatus.RUNNING


def test_second_start_is_rejected_while_guild_is_connecting():
    cog = DiscordCog(create_bot())
    cog.show_message = AsyncMock()
    cog.get_session(1).starting = True
    ctx = AsyncMock()
    ctx.guild = SimpleNamespace(id=1)

    asyncio.run(cog.start.callback(cog, ctx))

    cog.show_message.assert_awaited_once()
    assert "já está rodando" in cog.show_message.await_args.args[1]


def test_two_guild_stages_can_run_concurrently(monkeypatch):
    cog = DiscordCog(create_bot())
    cog.play_sound = MagicMock()
    first = cog.get_session(1)
    second = cog.get_session(2)
    first_message = AsyncMock()
    second_message = AsyncMock()
    first_message.edit = AsyncMock(return_value=first_message)
    second_message.edit = AsyncMock(return_value=second_message)
    first_ctx = AsyncMock()
    second_ctx = AsyncMock()
    first_ctx.send = AsyncMock(return_value=first_message)
    second_ctx.send = AsyncMock(return_value=second_message)
    original_sleep = asyncio.sleep

    async def instant_sleep(_seconds):
        await original_sleep(0)

    monkeypatch.setattr("FocoBot.discord_cog.asyncio.sleep", instant_sleep)

    async def run_stages():
        await asyncio.gather(
            cog.run_stage(
                first,
                first_ctx,
                AsyncMock(),
                phase="foco",
                duration=2,
                color=COLOR_SUCCESS,
                sound="start",
            ),
            cog.run_stage(
                second,
                second_ctx,
                AsyncMock(),
                phase="foco",
                duration=3,
                color=COLOR_SUCCESS,
                sound="start",
            ),
        )

    asyncio.run(run_stages())

    assert first.timer.get_status() == TimerStatus.EXPIRED
    assert first.timer.get_ticks() == 2
    assert second.timer.get_status() == TimerStatus.EXPIRED
    assert second.timer.get_ticks() == 3
    first_message.edit.assert_awaited()
    second_message.edit.assert_awaited()


def test_configure_command_updates_authorized_guild():
    cog = DiscordCog(create_bot())
    ctx = AsyncMock()
    ctx.guild = SimpleNamespace(id=123)
    ctx.author = SimpleNamespace(guild_permissions=SimpleNamespace(manage_guild=True))

    asyncio.run(cog.configure.callback(cog, ctx, 50, 10, 20, 3))

    config = cog.get_config(123)
    assert config.focus_minutes == 50
    assert config.short_break_minutes == 10
    assert config.long_break_minutes == 20
    assert config.rounds_before_long_break == 3
    ctx.send.assert_awaited_once()


def test_configure_command_rejects_unauthorized_member():
    cog = DiscordCog(create_bot())
    cog.show_message = AsyncMock()
    ctx = AsyncMock()
    ctx.guild = SimpleNamespace(id=123)
    ctx.author = SimpleNamespace(guild_permissions=SimpleNamespace(manage_guild=False))

    asyncio.run(cog.configure.callback(cog, ctx, 50, 10, 20, 3))

    assert cog.get_config(123).focus_minutes == 25
    cog.show_message.assert_awaited_once()
