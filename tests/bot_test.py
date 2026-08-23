import asyncio
from unittest.mock import AsyncMock

from FocoBot.__main__ import create_bot
from FocoBot.discord_cog import SOUNDS


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
