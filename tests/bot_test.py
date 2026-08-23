import asyncio

from FocoBot.__main__ import create_bot
from FocoBot.discord_cog import SOUNDS


def test_bot_uses_required_intents_and_preserves_prefix():
    bot = create_bot()

    assert bot.command_prefix == "!"
    assert bot.intents.message_content is True


def test_setup_hook_registers_legacy_commands():
    bot = create_bot()

    asyncio.run(bot.setup_hook())

    assert {command.name for command in bot.commands} == {
        "ajuda",
        "começar",
        "encerrar",
        "parar",
        "tempo",
    }
    assert bot.get_command("comecar").name == "começar"


def test_audio_assets_are_resolved_from_the_project():
    assert all(path.is_file() for path in SOUNDS.values())
