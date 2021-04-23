import asyncio
import discord
import os
from dotenv import load_dotenv #Biblioteca que auxilia a conexão do api token
from discord.ext import commands

load_dotenv()#carrega todos os arquivos .env

#client = discord.Client()
bot = commands.Bot(command_prefix='!')

#@client.event
@bot.event
async def on_ready():
    print('Estamos logados como: {}'.format(bot.user))

#@client.event
@bot.command(name="start", help="Inicia o foco ")
async def start_timer(ctx):
    start_work_em = discord.Embed(title= "Hora de começar a focar!", color=0x33c633)
    await ctx.send(embed = start_work_em)
    await asyncio.sleep(5)
    start_play_em = discord.Embed(title="Hora de começar sua pausa!", color=0x33c633)
    await ctx.send(embed = start_play_em)

@bot.command(name="stop", help="Para o foco ")
async def stop_timer(ctx):
    stop_timer_em = discord.Embed(title= "Hora de tirar uma pausa!", color=0x633333)
    await ctx.send(embed = stop_timer_em)

#client.run(os.environ['BOT_TOKEN'])
bot.run(os.environ['BOT_TOKEN'])