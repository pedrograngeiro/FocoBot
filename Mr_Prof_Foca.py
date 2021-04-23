import asyncio
import discord
import os
from timer import  Timer
from dotenv import load_dotenv #Biblioteca que auxilia a conexão do api token
from discord.ext import commands

load_dotenv()#carrega todos os arquivos .env

#client = discord.Client()
bot = commands.Bot(command_prefix='!')

timer = Timer()

#@client.event
@bot.event
async def on_ready():
    print('Estamos logados como: {}'.format(bot.user))

#@client.event
@bot.command(name="start", help="Inicia o foco ")
async def start_timer(ctx):
    start_work_em = discord.Embed(title= "Hora de começar a focar!", color=0x33c633)
    await ctx.send(embed = start_work_em)


    timer.start()
    while timer.get_status():
        await asyncio.sleep(1) #25 x 60
        timer.tick()
        if timer.get_ticks() >= 10:
            timer.stop()

    start_play_em = discord.Embed(title="Hora de começar sua pausa!", color=0x33c633)
    await ctx.send(embed = start_play_em)

@bot.command(name="stop", help="Para o foco ")
async def stop_timer(ctx):
    stop_timer_em = discord.Embed(title= "Hora de tirar uma pausa!", color=0x633333)
    await ctx.send(embed = stop_timer_em)
    timer.stop()



@bot.command(name="time", help="Show current time ")
async def show_time(ctx):

    await ctx.send(f"Current time status is: {timer.get_ticks()}")
    await ctx.send(f"Current time is: {timer.get_ticks()}")

@bot.command(name="help2", help="Show help text")
async def show_help(ctx):
    help_commands = dict()
    for command in bot.commands:
        help_commands[command.name] = command.help
    description = "Os comandos do bot são: {}".format(help_commands)
    show_help_em = discord.Embed(title= "Este é o Professor foca, um bot de sprints!", description=description, color=0x633333)
    await ctx.send(embed = show_help_em)


#client.run(os.environ['BOT_TOKEN'])
bot.run(os.environ['BOT_TOKEN'])