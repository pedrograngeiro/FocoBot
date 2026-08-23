import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from FocoBot.discord_cog import DiscordCog


class FocoBot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", help_command=None, intents=intents)

    async def setup_hook(self) -> None:
        await self.add_cog(DiscordCog(self))


def create_bot() -> FocoBot:
    return FocoBot()


def main() -> None:
    load_dotenv()
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError(
            "BOT_TOKEN não foi definido. Crie um arquivo .env a partir de .env.example."
        )

    create_bot().run(token)


if __name__ == "__main__":
    main()
