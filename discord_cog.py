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

    @commands.command(name="começar", help="Inicia o tempo de foco")
    async def start(self, ctx):
        if self.timer.get_status() == TimerStatus.RUNNING:
            await self.show_message(ctx, "O bot de foco já esta rodando! ", COLOR_SUCCESS)
            return

        await self.show_message(ctx, "Hora de começar a focar!\n"
                                     "25 minutos", COLOR_SUCCESS)
        self.timer.start(max_ticks=10)
        while self.timer.get_status() == TimerStatus.RUNNING:
            await asyncio.sleep(1)
            self.timer.tick()
        if self.timer.get_status() == TimerStatus.EXPIRED:
            await self.show_message(ctx, "Hora da pausa!\n"
                                         "5 minutos", COLOR_SUCCESS)
            self.timer.start(max_ticks=10)
            while self.timer.get_status() == TimerStatus.RUNNING:
                await asyncio.sleep(1)
                self.timer.tick()
            if self.timer.get_status() == TimerStatus.EXPIRED:
                await self.show_message(ctx, "Round finalizado!", COLOR_SUCCESS)


    async def show_message(self, ctx, title, color):
        start_work_em = discord.Embed(title=title, color=color)
        await ctx.send(embed=start_work_em)

    @commands.command(name="parar", help="Finalizar o foco! ")
    async def stop(self, ctx):
        if self.timer.get_status() != TimerStatus.RUNNING:
            await self.show_message(ctx, "O focobot já está parado, você deveria iniciar o cronômetro antes de "
                                         "pará-lo! ", COLOR_SUCCESS)
            return
        await self.show_message(ctx, "Hora de fazer uma pausa!", COLOR_DANGER)
        self.timer.stop()

    @commands.command(name="tempo", help="Mostra o tempo atual! ")
    async def show_time(self, ctx):
        if self.timer.get_status() == TimerStatus.INICIALIZADO:
            self.tempo = 'ONLINE'

        if self.timer.get_status() == TimerStatus.RODANDO:
            self.tempo = 'RODANDO'

        if self.timer.get_status() == TimerStatus.PARADO:
            self.tempo = 'PARADO'

        if self.timer.get_status() == TimerStatus.FINALIZADO:
            self.tempo = 'FINALIZADO'

        await self.show_message(ctx, f"Estamos no round: {self.round} \n"
                                     f"O tempo é: {self.timer.get_ticks()}", COLOR_SUCCESS)

    @commands.command(name="ajuda", help="Mostra as funções de cada comando! ")
    async def show_help(self, ctx):
        help_commands = dict()
        for command in self.bot.commands:
            help_commands[command.name] = command.help
        description = "Os comandos do bot são: {}".format(help_commands)

        show_help_em = discord.Embed(title="Este é o Professor foca, um bot de sprints!", description=description,
                                     color=COLOR_SUCCESS)
        await ctx.send(embed=show_help_em)
