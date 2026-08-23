import asyncio
from pathlib import Path

import discord
from discord import FFmpegPCMAudio, PCMVolumeTransformer
from discord.ext import commands

from FocoBot.timer import Timer, TimerStatus

COLOR_DANGER = 0xFF6F69
COLOR_SUCCESS = 0x88D8B0
COLOR_PAUSE = 0xFFCC5C
COLOR_EXPIRED = 0xFC3468
WORK_SECONDS = 25 * 60
SHORT_BREAK_SECONDS = 5 * 60
LONG_BREAK_SECONDS = 10 * 60
LONG_BREAK_EVERY = 4
SOUNDS_DIR = Path(__file__).resolve().parents[1] / "sounds"
SOUNDS = {
    "start": SOUNDS_DIR / "start2.mp3",
    "short_break": SOUNDS_DIR / "short-break_fixed.mp3",
    "long_break": SOUNDS_DIR / "long-break_fixed.mp3",
}


class DiscordCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.timer = Timer()
        self.round = 0

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        print(f"Estamos logados como: {self.bot.user}")

    @commands.command(name="começar", aliases=["comecar"], help="Inicia o tempo de foco")
    async def start(self, ctx: commands.Context) -> None:
        if self.timer.get_status() == TimerStatus.RUNNING:
            await self.show_message(ctx, "O bot de foco já está rodando!", COLOR_SUCCESS)
            return

        author_voice = getattr(ctx.author, "voice", None)
        if not author_voice:
            await ctx.send("Entre em um canal de voz para usar o FocoBot.")
            return

        channel = author_voice.channel
        voice = ctx.voice_client
        if voice is None:
            voice = await channel.connect()
        elif voice.channel != channel:
            await voice.move_to(channel)

        while True:
            await self.show_message(ctx, "Hora de começar a focar!\n25 minutos", COLOR_SUCCESS)
            self.play_sound(voice, "start")

            self.timer.start(max_ticks=WORK_SECONDS)
            self.add_round()
            while self.timer.get_status() == TimerStatus.RUNNING:
                await asyncio.sleep(1)
                self.timer.tick()

            if self.timer.get_status() == TimerStatus.EXPIRED:
                if self.round % LONG_BREAK_EVERY == 0:
                    await self.show_message(ctx, "Hora da pausa longa!\n10 minutos", COLOR_PAUSE)
                    self.play_sound(voice, "long_break")
                    self.timer.start(max_ticks=LONG_BREAK_SECONDS)
                else:
                    await self.show_message(ctx, "Hora da pausa!\n5 minutos", COLOR_PAUSE)
                    self.play_sound(voice, "short_break")
                    self.timer.start(max_ticks=SHORT_BREAK_SECONDS)

                while self.timer.get_status() == TimerStatus.RUNNING:
                    await asyncio.sleep(1)
                    self.timer.tick()
                if self.timer.get_status() == TimerStatus.EXPIRED:
                    await self.show_message(ctx, f"Round {self.round} finalizado!", COLOR_SUCCESS)
            if self.timer.get_status() == TimerStatus.STOPPED:
                break

    @staticmethod
    def play_sound(voice: discord.VoiceClient, sound: str) -> None:
        source = FFmpegPCMAudio(str(SOUNDS[sound]))
        voice.play(PCMVolumeTransformer(source, volume=0.2))

    async def show_message(self, ctx: commands.Context, title: str, color: int) -> None:
        message = discord.Embed(title=title, color=color)
        await ctx.send(embed=message)

    def add_round(self) -> None:
        self.round += 1

    @commands.command(
        name="parar", help="Finalizar o foco! Atenção! (Não encerra o número de rounds)"
    )
    async def stop(self, ctx: commands.Context) -> None:
        if self.timer.get_status() != TimerStatus.RUNNING:
            await self.show_message(
                ctx,
                "O focobot já está parado, você deveria iniciar o cronômetro antes de pará-lo!",
                COLOR_SUCCESS,
            )
            return
        await self.show_message(ctx, "Hora de fazer uma pausa!", COLOR_DANGER)
        self.timer.stop()
        if ctx.voice_client:
            await ctx.voice_client.disconnect()

    @commands.command(name="encerrar", help="Finalizar o foco! (Zerando o número de rounds!)")
    async def end(self, ctx: commands.Context) -> None:
        if self.timer.get_status() != TimerStatus.RUNNING:
            await self.show_message(
                ctx,
                "O focobot já está parado, você deveria iniciar o cronômetro antes de pará-lo!",
                COLOR_SUCCESS,
            )
            return
        self.round = 0
        await self.show_message(
            ctx, "Muito obrigado por utilizar o FocoBot!\nBom descanso!", COLOR_DANGER
        )
        self.timer.stop()
        if ctx.voice_client:
            await ctx.voice_client.disconnect()

    @commands.command(name="tempo", help="Mostra o tempo atual! ")
    async def show_time(self, ctx: commands.Context) -> None:
        await self.show_message(
            ctx,
            f"Estamos no round: {self.round} \nO tempo é: {self.timer.convert_ticks()}",
            COLOR_SUCCESS,
        )

    @commands.command(name="ajuda", help="Mostra as funções de cada comando! ")
    async def show_help(self, ctx: commands.Context) -> None:
        description = "\n".join(
            f"`!{command.name}` — {command.help}" for command in self.bot.commands
        )
        message = discord.Embed(
            title="Este é o Professor Foca, um bot de sprints!",
            description=description,
            color=COLOR_SUCCESS,
        )
        await ctx.send(embed=message)
