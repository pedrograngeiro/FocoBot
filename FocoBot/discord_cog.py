import asyncio
import logging
from pathlib import Path

import discord
from discord import FFmpegPCMAudio, PCMVolumeTransformer
from discord.ext import commands

from FocoBot.config import PomodoroConfig
from FocoBot.timer import Timer, TimerStatus

LOGGER = logging.getLogger(__name__)

COLOR_DANGER = 0xFF6F69
COLOR_SUCCESS = 0x88D8B0
COLOR_PAUSE = 0xFFCC5C
COLOR_EXPIRED = 0xFC3468
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
        self.configurations: dict[int, PomodoroConfig] = {}

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
        guild_id = ctx.guild.id
        channel = author_voice.channel
        voice = ctx.voice_client
        if voice is None:
            voice = await channel.connect()
        elif voice.channel != channel:
            await voice.move_to(channel)

        while True:
            config = self.get_config(guild_id)
            self.add_round()
            await self.run_stage(
                ctx,
                voice,
                phase="foco",
                duration=config.focus_seconds,
                color=COLOR_SUCCESS,
                sound="start",
            )

            if self.timer.get_status() == TimerStatus.EXPIRED:
                config = self.get_config(guild_id)
                if self.round % config.rounds_before_long_break == 0:
                    await self.run_stage(
                        ctx,
                        voice,
                        phase="pausa longa",
                        duration=config.long_break_seconds,
                        color=COLOR_PAUSE,
                        sound="long_break",
                    )
                else:
                    await self.run_stage(
                        ctx,
                        voice,
                        phase="pausa curta",
                        duration=config.short_break_seconds,
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

    def get_config(self, guild_id: int) -> PomodoroConfig:
        return self.configurations.setdefault(guild_id, PomodoroConfig())

    def build_config_embed(
        self, config: PomodoroConfig, title: str = "Configuração do Pomodoro"
    ) -> discord.Embed:
        embed = discord.Embed(title=title, color=COLOR_SUCCESS)
        embed.add_field(name="Foco", value=f"{config.focus_minutes} min", inline=True)
        embed.add_field(name="Pausa curta", value=f"{config.short_break_minutes} min", inline=True)
        embed.add_field(name="Pausa longa", value=f"{config.long_break_minutes} min", inline=True)
        embed.add_field(
            name="Pausa longa a cada",
            value=f"{config.rounds_before_long_break} ciclos",
            inline=False,
        )
        if self.timer.is_active():
            embed.set_footer(text="Os novos valores entram na próxima etapa")
        return embed

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

    @commands.hybrid_command(
        name="configuracao", aliases=["config", "tempos"], help="Mostra os tempos configurados"
    )
    async def show_config(self, ctx: commands.Context) -> None:
        if ctx.guild is None:
            await self.show_message(ctx, "Use este comando em um servidor.", COLOR_DANGER)
            return
        await ctx.send(embed=self.build_config_embed(self.get_config(ctx.guild.id)))

    @commands.hybrid_command(name="configurar", help="Altera os tempos do Pomodoro")
    @discord.app_commands.describe(
        foco="Minutos de foco (1–180)",
        pausa="Minutos de pausa curta (1–60)",
        longa="Minutos de pausa longa (1–60)",
        ciclos="Ciclos até a pausa longa (1–12)",
    )
    async def configure(
        self,
        ctx: commands.Context,
        foco: int,
        pausa: int,
        longa: int,
        ciclos: int,
    ) -> None:
        if ctx.guild is None:
            await self.show_message(ctx, "Use este comando em um servidor.", COLOR_DANGER)
            return

        permissions = getattr(ctx.author, "guild_permissions", None)
        if permissions is None or not permissions.manage_guild:
            await self.show_message(
                ctx, "Você precisa da permissão Gerenciar Servidor.", COLOR_DANGER
            )
            return

        try:
            config = PomodoroConfig(
                focus_minutes=foco,
                short_break_minutes=pausa,
                long_break_minutes=longa,
                rounds_before_long_break=ciclos,
            )
        except ValueError as error:
            await self.show_message(ctx, f"Configuração inválida: {error}.", COLOR_DANGER)
            return

        self.configurations[ctx.guild.id] = config
        await ctx.send(embed=self.build_config_embed(config, title="Configuração atualizada"))

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
