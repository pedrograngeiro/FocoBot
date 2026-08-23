import asyncio
from unittest.mock import AsyncMock

from FocoBot.__main__ import create_bot
from FocoBot.discord_cog import (
    COLOR_SUCCESS,
    SOUNDS,
    DiscordCog,
    make_progress_bar,
)


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
        "encerrar",
        "parar",
        "pausar",
        "pular",
        "retomar",
        "tempo",
    }
    assert bot.get_command("começar").name == "comecar"
    assert bot.get_command("foco").name == "comecar"
    bot.tree.sync.assert_awaited_once_with()


def test_hybrid_commands_expose_application_commands():
    bot = create_bot()
    bot.tree.sync = AsyncMock()

    asyncio.run(bot.setup_hook())

    assert {command.name for command in bot.tree.get_commands()} == {
        "ajuda",
        "comecar",
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
    cog.round = 2
    cog.phase = "foco"
    cog.timer_color = COLOR_SUCCESS
    cog.timer.start(max_ticks=10)
    for _ in range(4):
        cog.timer.tick()

    embed = cog.build_timer_embed().to_dict()

    assert embed["title"].endswith("Foco")
    assert embed["description"] == "`████░░░░░░░░`"
    assert embed["fields"] == [
        {"inline": True, "name": "Restante", "value": "00:06"},
        {"inline": True, "name": "Decorrido", "value": "00:04"},
        {"inline": True, "name": "Status", "value": "Rodando"},
    ]
    assert embed["footer"]["text"].startswith("Round 2")

    cog.timer.tick()
    assert cog.build_timer_embed().title.startswith("◓")


def test_paused_timer_embed_uses_static_indicator():
    cog = DiscordCog(create_bot())
    cog.phase = "pausa curta"
    cog.timer.start(max_ticks=10)
    cog.timer.pause()

    embed = cog.build_timer_embed().to_dict()

    assert embed["title"] == "⏸ Pausa Curta"
    assert embed["fields"][2]["value"] == "Pausado"


def test_refresh_timer_message_edits_the_existing_message():
    cog = DiscordCog(create_bot())
    original_message = AsyncMock()
    updated_message = AsyncMock()
    original_message.edit = AsyncMock(return_value=updated_message)
    cog.timer_message = original_message

    asyncio.run(cog.refresh_timer_message())

    original_message.edit.assert_awaited_once()
    assert cog.timer_message is updated_message
