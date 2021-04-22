import discord
import os
from dotenv import load_dotenv
from discord.ext import commands




load_dotenv()

#client = discord.Client()
bot = commands.Bot(command_prefix='!')

#@client.event
@bot.event
async def on_ready():
    print('We have logged in as {}'.format(bot.user))

#@client.event
@bot.command(name="start", help="Inicia o foco ")
async def start_timer(ctx):
    await ctx.send("Hora de focar!")
    """
    if message.author == client.user:
        return
    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')
    """

#client.run(os.environ['BOT_TOKEN'])
bot.run(os.environ['BOT_TOKEN'])