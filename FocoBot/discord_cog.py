import asyncio
import logging
from pathlib import Path

import discord
from discord import FFmpegPCMAudio, PCMVolumeTransformer
from discord.ext import commands

from FocoBot.timer import Timer, TimerStatus

LOGGER = logging.getLogger(__name__)

COLOR_DANGER = 0xFF6F69
COLOR_SUCCESS = 0x88D8B0
COLOR_PAUSE = 0xFFCC5C
COLOR_EXPIRED = 0xFC3468
WORK_SECONDS = 25 * 60
SHORT_BREAK_SECONDS = 5 * 60
LONG_BREAK_SECONDS = 10 * 60
LONG_BREAK_EVERY = 4
TIMER_UPDATE_INTERVAL = 5
PROGRESS_BAR_LENGTH = 12
ANIMATION_FRAMES = ("◐", "◓", "◑", "◒")
SOUNDS_DIR = Path(__file__).resolve().parents[1] / "sounds"
SOUNDS = {
    "start": SOUNDS_DIR / "start2.mp3",
    "short_break": SOUNDS_DIR / "short-break_fixed.mp3",
    "long_break": SOUNDS_DIR / "long-break_fixed.mp3",
}
STATUS_LABELS = {
    TimerStatus.INITIALIZED: "aguardando",
    TimerStatus.RUNNING: "rodando",
    TimerStatus.PAUSED: "pausado",
    TimerStatus.STOPPED: "parado",
    TimerStatus.EXPIRED: "finalizado",
}


def make_progress_bar(elapsed: int, total: int, length: int = PROGRESS_BAR_LENGTH) -> str:
    progress = min(1.0, elapsed / total) if total > 0 else 0.0
    filled = int(progress * length)
    return "█" * filled + "░" * (length - filled)


class DiscordCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.timer = Timer()
        self.round = 0
        self.phase = "aguardando"
        self.timer_message: discord.Message | None = None
        self.timer_color = COLOR_SUCCESS

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        print(f"Estamos logados como: {self.bot.user}")

    @commands.hybrid_command(
        name="comecar", aliases=["começar", "foco"], help="Inicia o tempo de foco"
    )
    async def start(self, ctx: commands.Context) -> None:
        if self.timer.is_active():
            await self.show_message(ctx, "O bot de foco já está rodando!", COLOR_SUCCESS)
            return

        author_voice = getattr(ctx.author, "voice", None)
        if not author_voice:
            await ctx.send("Entre em um canal de voz para usar o FocoBot.")
            return

        await ctx.defer()
        channel = author_voice.channel
        voice = ctx.voice_client
        if voice is None:
            voice = await channel.connect()
        elif voice.channel != channel:
            await voice.move_to(channel)

        while True:
            self.add_round()
            await self.run_stage(
                ctx,
                voice,
                phase="foco",
                duration=WORK_SECONDS,
                color=COLOR_SUCCESS,
                sound="start",
            )

            if self.timer.get_status() == TimerStatus.EXPIRED:
                if self.round % LONG_BREAK_EVERY == 0:
                    await self.run_stage(
                        ctx,
                        voice,
                        phase="pausa longa",
                        duration=LONG_BREAK_SECONDS,
                        color=COLOR_PAUSE,
                        sound="long_break",
                    )
                else:
                    await self.run_stage(
                        ctx,
                        voice,
                        phase="pausa curta",
                        duration=SHORT_BREAK_SECONDS,
                        color=COLOR_PAUSE,
                        sound="short_break",
                    )
                if self.timer.get_status() == TimerStatus.EXPIRED:
                    await self.show_message(ctx, f"Round {self.round} finalizado!", COLOR_SUCCESS)
            if self.timer.get_status() == TimerStatus.STOPPED:
                break

    async def run_stage(
        self,
        ctx: commands.Context,
        voice: discord.VoiceClient,
        *,
        phase: str,
        duration: int,
        color: int,
        sound: str,
    ) -> None:
        self.phase = phase
        self.timer_color = color
        self.timer.start(max_ticks=duration)
        self.play_sound(voice, sound)
        self.timer_message = await ctx.send(embed=self.build_timer_embed())

        seconds_since_update = 0
        while self.timer.is_active():
            await asyncio.sleep(1)
            self.timer.tick()
            seconds_since_update += 1
            if seconds_since_update >= TIMER_UPDATE_INTERVAL or not self.timer.is_active():
                await self.refresh_timer_message()
                seconds_since_update = 0

    def build_timer_embed(self) -> discord.Embed:
        status = self.timer.get_status()
        if status == TimerStatus.PAUSED:
            indicator = "⏸"
        elif status == TimerStatus.STOPPED:
            indicator = "⏹"
        elif status == TimerStatus.EXPIRED:
            indicator = "✓"
        else:
            frame = (self.timer.get_ticks() // TIMER_UPDATE_INTERVAL) % len(ANIMATION_FRAMES)
            indicator = ANIMATION_FRAMES[frame]

        progress = make_progress_bar(
            self.timer.get_ticks(), self.timer.max_ticks, PROGRESS_BAR_LENGTH
        )
        embed = discord.Embed(
            title=f"{indicator} {self.phase.title()}",
            description=f"`{progress}`",
            color=self.timer_color,
        )
        embed.add_field(name="Restante", value=self.timer.convert_remaining_ticks(), inline=True)
        embed.add_field(name="Decorrido", value=self.timer.convert_ticks(), inline=True)
        embed.add_field(name="Status", value=STATUS_LABELS[status].title(), inline=True)
        embed.set_footer(
            text=f"Round {self.round} • atualização a cada {TIMER_UPDATE_INTERVAL} segundos"
        )
        return embed

    async def refresh_timer_message(self) -> None:
        if self.timer_message is None:
            return
        try:
            self.timer_message = await self.timer_message.edit(embed=self.build_timer_embed())
        except discord.HTTPException:
            LOGGER.exception("Não foi possível atualizar a mensagem do cronômetro")
            self.timer_message = None

    @staticmethod
    def play_sound(voice: discord.VoiceClient, sound: str) -> None:
        source = FFmpegPCMAudio(str(SOUNDS[sound]))
        voice.play(PCMVolumeTransformer(source, volume=0.2))

    async def show_message(self, ctx: commands.Context, title: str, color: int) -> None:
        message = discord.Embed(title=title, color=color)
        await ctx.send(embed=message)

    def add_round(self) -> None:
        self.round += 1

    @commands.hybrid_command(
        name="parar", help="Finalizar o foco! Atenção! (Não encerra o número de rounds)"
    )
    async def stop(self, ctx: commands.Context) -> None:
        if not self.timer.is_active():
            await self.show_message(
                ctx,
                "O focobot já está parado, você deveria iniciar o cronômetro antes de pará-lo!",
                COLOR_SUCCESS,
            )
            return
        await self.show_message(ctx, "Hora de fazer uma pausa!", COLOR_DANGER)
        self.timer.stop()
        self.phase = "parado"
        await self.refresh_timer_message()
        if ctx.voice_client:
            await ctx.voice_client.disconnect()

    @commands.hybrid_command(
        name="encerrar", help="Finalizar o foco! (Zerando o número de rounds!)"
    )
    async def end(self, ctx: commands.Context) -> None:
        if not self.timer.is_active():
            await self.show_message(
                ctx,
                "O focobot já está parado, você deveria iniciar o cronômetro antes de pará-lo!",
                COLOR_SUCCESS,
            )
            return
        self.round = 0
        self.phase = "parado"
        await self.show_message(
            ctx, "Muito obrigado por utilizar o FocoBot!\nBom descanso!", COLOR_DANGER
        )
        self.timer.stop()
        await self.refresh_timer_message()
        if ctx.voice_client:
            await ctx.voice_client.disconnect()

    @commands.hybrid_command(name="pausar", help="Pausa a etapa atual")
    async def pause(self, ctx: commands.Context) -> None:
        if not self.timer.pause():
            await self.show_message(ctx, "Não há uma etapa rodando para pausar.", COLOR_DANGER)
            return
        await self.refresh_timer_message()
        await self.show_message(ctx, "Cronômetro pausado.", COLOR_PAUSE)

    @commands.hybrid_command(name="retomar", help="Retoma a etapa pausada")
    async def resume(self, ctx: commands.Context) -> None:
        if not self.timer.resume():
            await self.show_message(ctx, "O cronômetro não está pausado.", COLOR_DANGER)
            return
        await self.refresh_timer_message()
        await self.show_message(ctx, "Cronômetro retomado!", COLOR_SUCCESS)

    @commands.hybrid_command(name="pular", help="Pula a etapa atual")
    async def skip(self, ctx: commands.Context) -> None:
        if not self.timer.expire():
            await self.show_message(ctx, "Não há uma etapa ativa para pular.", COLOR_DANGER)
            return
        await self.refresh_timer_message()
        await self.show_message(ctx, f"Etapa de {self.phase} pulada.", COLOR_EXPIRED)

    @commands.hybrid_command(name="tempo", help="Mostra o estado e o tempo atual")
    async def show_time(self, ctx: commands.Context) -> None:
        status = STATUS_LABELS[self.timer.get_status()]
        await self.show_message(
            ctx,
            f"Round: {self.round}\n"
            f"Etapa: {self.phase}\n"
            f"Status: {status}\n"
            f"Restante: {self.timer.convert_remaining_ticks()}\n"
            f"Decorrido: {self.timer.convert_ticks()}",
            COLOR_SUCCESS,
        )

    @commands.hybrid_command(name="ajuda", help="Mostra as funções de cada comando")
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
