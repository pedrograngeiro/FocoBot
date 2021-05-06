import asyncio
import discord
from timer import Timer, TimerStatus
from dotenv import load_dotenv
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
        # round 1
        if self.timer.get_status() == TimerStatus.RODANDO:
            await self.show_message(ctx, "O bot de foco já esta rodando! ", COLOR_SUCCESS)
            return
        await self.show_message(ctx, "Hora de começar a focar! Intervalo de 25 minutos ", COLOR_SUCCESS)
        self.timer.start(max_ticks=15)

        await self.running()
        self.timer.add_round()

        self.tempo = 'Hora de descansar! Intervalo de 5 minutos'
        await self.show_message(ctx, f"O bot está: {self.tempo}", COLOR_SUCCESS)
        self.timer.start(max_ticks=30)

        await self.running()
        self.timer.add_round()
        # fim round 1

    async def show_message(self, ctx, title, color):
        start_work_em = discord.Embed(title=title, color=color)
        await ctx.send(embed=start_work_em)

    async def running(self):
        while self.timer.get_status() == TimerStatus.RODANDO:
            await asyncio.sleep(1)
            self.timer.tick()

    @commands.command()
    async def stop(self, ctx):
        if self.timer.get_status() != TimerStatus.RODANDO:
            await self.show_message(ctx, "O bot já está pausado! ", COLOR_SUCCESS)
            return
        await self.show_message(ctx, "Hora de fazer uma pausa!", COLOR_DANGER)
        self.timer.stop()

    @commands.command()
    async def mostrar_tempo(self, ctx):

        if self.timer.get_status() == TimerStatus.INICIALIZADO:
            self.tempo = 'ONLINE'

        if self.timer.get_status() == TimerStatus.RODANDO:
            self.tempo = 'RODANDO'

        if self.timer.get_status() == TimerStatus.PARADO:
            self.tempo = 'PARADO'

        if self.timer.get_status() == TimerStatus.FINALIZADO:
            self.tempo = 'FINALIZADO'

        await self.show_message(ctx, f"Estamos no round: {self.timer.round} \n"
                                     f"O tempo é: {self.timer.get_ticks()}", COLOR_SUCCESS)

    @commands.command()
    async def show_help(self, ctx):
        help_commands = dict()
        for command in self.bot.commands:
            help_commands[command.name] = command.help
        description = "Os comandos do bot são: {}".format(help_commands)

        show_help_em = discord.Embed(title="Este é o Professor foca, um bot de sprints!", description=description,
                                     color=COLOR_SUCCESS)
        await ctx.send(embed=show_help_em)
