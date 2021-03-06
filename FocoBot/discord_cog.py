import asyncio
import sys
import discord
from FocoBot.timer import Timer, TimerStatus
from dotenv import load_dotenv
from discord.ext import commands
from discord import FFmpegPCMAudio
from discord import PCMVolumeTransformer

COLOR_DANGER = 0xff6f69
COLOR_SUCCESS = 0x88d8b0
COLOR_PAUSE = 0xffcc5c
COLOR_EXPIRED = 0xFC3468


class DiscordCog(commands.Cog):

    def __init__(self, bot):

        self.bot = bot
        self.timer = Timer()
        self.round = 0
        #self.numero_de_segundos = 0


    @commands.Cog.listener()
    async def on_ready(self):
        print('Estamos logados como: {}'.format(self.bot.user))

    @commands.command(name="começar", help="Inicia o tempo de foco")
    async def start(self, ctx):
        if self.timer.get_status() == TimerStatus.RUNNING:
            await self.show_message(ctx, "O bot de foco já esta rodando! ", COLOR_SUCCESS)
            return

        #conecta no canal de voz
        if (ctx.author.voice):
            channel = ctx.message.author.voice.channel
            voice = await channel.connect()
            # caminho dos audios
            sound = {
                'start': '../sounds/start2.mp3',
                'short_break': '../sounds/short-break_fixed.mp3',
                'long_break': '../sounds/long-break_fixed.mp3',
            }

            while True:
                await self.show_message(ctx, "Hora de começar a focar!\n"
                                             "25 minutos", COLOR_SUCCESS)
                voice.play(PCMVolumeTransformer(FFmpegPCMAudio(sound['start']), volume=0.2))

                self.timer.start(max_ticks=1500) #1500
                self.add_round()
                while self.timer.get_status() == TimerStatus.RUNNING:
                    await asyncio.sleep(1)
                    self.timer.tick()
                if self.timer.get_status() == TimerStatus.EXPIRED:
                    if self.round % 3 == 0:
                        await self.show_message(ctx, "Hora da pausa longa!\n"
                                                    "10 minutos", COLOR_PAUSE)
                        voice.play(PCMVolumeTransformer(FFmpegPCMAudio(sound['long_break']), volume=0.2))
                        self.timer.start(max_ticks=600) #600
                    else:
                        await self.show_message(ctx, "Hora da pausa!\n"
                                                    "5 minutos", COLOR_PAUSE)
                        voice.play(PCMVolumeTransformer(FFmpegPCMAudio(sound['short_break']), volume=0.2))
                        self.timer.start(max_ticks=300) #300
                    while self.timer.get_status() == TimerStatus.RUNNING:
                        await asyncio.sleep(1)
                        self.timer.tick()
                    if self.timer.get_status() == TimerStatus.EXPIRED:
                        await self.show_message(ctx, f"Round {self.round} finalizado!", COLOR_SUCCESS)
                if self.timer.get_status() == TimerStatus.STOPPED:
                    break
        else:
            await ctx.send('Entre no canal de voz para usar o Focobot.')
    async def show_message(self, ctx, title, color):
        start_work_em = discord.Embed(title=title, color=color)
        await ctx.send(embed=start_work_em)

    def add_round(self):
        self.round += 1


    @commands.command(name="parar", help="Finalizar o foco! Atenção! (Não encerra o número de rounds)")
    async def stop(self, ctx):
        if self.timer.get_status() != TimerStatus.RUNNING:
            await self.show_message(ctx, "O focobot já está parado, você deveria iniciar o cronômetro antes de "
                                         "pará-Dlo! ", COLOR_SUCCESS)
            return
        await self.show_message(ctx, "Hora de fazer uma pausa!", COLOR_DANGER)
        self.timer.stop()
        #disconecta do canal de voz
        if(ctx.voice_client):
            await ctx.guild.voice_client.disconnect()

    @commands.command(name="encerrar", help="Finalizar o foco! (Zerando o número de rounds!)")
    async def end(self, ctx):
        if self.timer.get_status() != TimerStatus.RUNNING:
            await self.show_message(ctx, "O focobot já está parado, você deveria iniciar o cronômetro antes de "
                                         "pará-Dlo! ", COLOR_SUCCESS)
            return
        self.round = 0  # Reseta o contador de rounds. Afinal você parou o bot
        await self.show_message(ctx, "Muito obrigado por utilizar o focobot!\n"
                                     "Bom descanso!", COLOR_DANGER)
        self.timer.stop()
        #disconecta do canal de voz
        if(ctx.voice_client):
            await ctx.guild.voice_client.disconnect()


    @commands.command(name="tempo", help="Mostra o tempo atual! ")
    async def show_time(self, ctx):
        if self.timer.get_status() == TimerStatus.INITIALIZED:
            self.tempo = 'ONLINE'

        if self.timer.get_status() == TimerStatus.RUNNING:
            self.tempo = 'RODANDO'

        if self.timer.get_status() == TimerStatus.STOPPED:
            self.tempo = 'PARADO'

        if self.timer.get_status() == TimerStatus.EXPIRED:
            self.tempo = 'FINALIZADO'

        self.timer.convert_ticks()
        await self.show_message(ctx, f"Estamos no round: {self.round} \n"
                                     f"O tempo é: {self.timer.min_seg}", COLOR_SUCCESS)

    @commands.command(name="ajuda", help="Mostra as funções de cada comando! ")
    async def show_help(self, ctx):
        help_commands = dict()
        for command in self.bot.commands:
            help_commands[command.name] = command.help
        description = "Os comandos do bot são: {}".format(help_commands)

        show_help_em = discord.Embed(title="Este é o Professor foca, um bot de sprints!", description=description,
                                     color=COLOR_SUCCESS)
        await ctx.send(embed=show_help_em)
