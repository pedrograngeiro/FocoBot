import asyncio
import discord
from timer import Timer
from discord.ext import commands

COLOR_DANGER = 0x633333
COLOR_SUCCESS = 0x33c633


class DiscordCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.timer = Timer()

    @commands.Cog.listener()
    async def on_ready(self):
        print('Estamos logados como: {}'.format(self.bot.user))

    @commands.command()
    async def start(self, ctx):
        await self.show_message(ctx, "Hora de começar a focar! ", COLOR_SUCCESS)
        self.timer.start()
        while self.timer.is_running():
            await asyncio.sleep(1)  # 25 x 60
            self.timer.tick()
        await self.show_message(ctx, "Hora de começar sua pausa! ", COLOR_SUCCESS)

    async def show_message(self, ctx, title, color):
        start_work_em = discord.Embed(title=title, color=color)
        await ctx.send(embed=start_work_em)

    @commands.command()
    async def stop(self, ctx):
        await show_message(ctx, "Hora de tirar uma pausa!", COLOR_DANGER)
        timer.stop()

    @commands.command()
    async def show_time(self, ctx):
        await ctx.send(f"Current time status is: {timer.get_ticks()}")
        await ctx.send(f"Current time is: {timer.get_ticks()}")

    @commands.command()
    async def show_help(self, ctx):
        help_commands = dict()
        for command in bot.commands:
            help_commands[command.name] = command.help
        description = "Os comandos do bot são: {}".format(help_commands)

        show_help_em = discord.Embed(title="Este é o Professor foca, um bot de sprints!", description=description,
                                     color=COLOR_SUCCESS)
        await ctx.send(embed=show_help_em)
