import asyncio
import discord
import os
from timer import Timer
from dotenv import load_dotenv  # Biblioteca que auxilia a conexão do api token
from discord.ext import commands

COLOR_DANGER = 0x633333

COLOR_SUCCESS = 0x33c633

load_dotenv()  # carrega todos os arquivos .env

bot = commands.Bot(command_prefix='!', help_command=None)
timer = Timer()


# @client.event
@bot.event
async def on_ready():
    print('Estamos logados como: {}'.format(bot.user))


# @client.event
@bot.command(name="start", help="Inicia o tempo de foco!")
async def start_timer(ctx):
    await show_message(ctx, "Hora de começar a focar! " , COLOR_SUCCESS)
    timer.start()
    while timer.is_running():
        await asyncio.sleep(1)  # 25 x 60
        timer.tick()
    await show_message(ctx, "Hora de começar sua pausa! ", COLOR_SUCCESS)


async def show_message(ctx, title, color ):
    start_work_em = discord.Embed(title=title, color=color)
    await ctx.send(embed=start_work_em)


@bot.command(name="stop", help="Finalizar o foco! ")
async def stop_timer(ctx):
    await show_message(ctx, "Hora de tirar uma pausa!", COLOR_DANGER)
    timer.stop()


@bot.command(name="time", help="Mostra o tempo atual! ")
async def show_time(ctx):
    await ctx.send(f"Current time status is: {timer.get_ticks()}")
    await ctx.send(f"Current time is: {timer.get_ticks()}")


@bot.command(name="help", help="Mostra as funções de cada comando! ")
async def show_help(ctx):
    help_commands = dict()
    for command in bot.commands:
        help_commands[command.name] = command.help
    description = "Os comandos do bot são: {}".format(help_commands)

    show_help_em = discord.Embed(title="Este é o Professor foca, um bot de sprints!", description=description,
                                 color=COLOR_SUCCESS)
    await ctx.send(embed=show_help_em)


bot.run(os.environ['BOT_TOKEN'])
