import time

import discord
from discord import FFmpegPCMAudio
from discord.ext import commands
import asyncio
from aiohttp import web  # aiohttp is used to run the Flask server asynchronously
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.default()
intents.message_content = True

# Initialize the Discord bot
bot = commands.Bot(command_prefix='!', intents=intents)
voice = None

# Initialize Flask application
app = web.Application()

# Define a route to handle incoming HTTP requests
async def handle(request):
    data = await request.json()  # Assuming incoming data is JSON
    print('Received data:', data)
    if "play" in data:
        global voice
        if voice:
            source = FFmpegPCMAudio(data['play'] + ".mp3")
            if source:
                voice.play(source)
            else:
                return web.Response(text='No valid audio file.', status=404)
    else:
        return web.Response(text="no dice", status=404)
    return web.Response(text='Received', status=200)

async def handle_filenames(request):
    data = await request.json()
    print('Received data: ', data)
    cwd = os.getcwd()
    files = os.listdir(cwd)

    mp3 = [file for file in files if file.endswith('.mp3')]
    mp3s = [file[:-4] for file in mp3]

    return mp3s

app.router.add_post('/webhook', handle)
app.router.add_get('/home', handle_filenames)

# Function to run the Flask server
async def run_flask():
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 5000)
    await site.start()
    print('Flask server running on http://0.0.0.0:5000')

# Command to start the Flask server
@bot.command()
async def start_server(ctx):
    await ctx.send('Starting server...')
    await run_flask()


@bot.command()
async def getfilenames(ctx):
    cwd = os.getcwd()
    files = os.listdir(cwd)

    mp3 = [file for file in files if file.endswith('.mp3')]
    mp3s = [file[:-4] for file in mp3]

    await ctx.send(mp3s)



@bot.command()
async def play(ctx, *, audio):
    # await ctx.send(f'You said: {audio}')
    if voice:
        source = FFmpegPCMAudio(audio + ".mp3")
        if source:
            voice.play(source)
        else:
            await ctx.send("No audio file called: " + audio + ".mp3")
    else:
        await ctx.send("Not connected to a VC. Type !join")

@bot.command()
async def join(ctx):
    global voice
    if ctx.author.voice:
        channel = ctx.message.author.voice.channel
        voice = await channel.connect()
    else:
        ctx.send("You are not in a VC.")


@bot.command()
async def leave(ctx):
    global voice
    if ctx.voice_client:
        if voice:
            source = FFmpegPCMAudio("nahallgood.mp3")
            voice.play(source)
            await asyncio.sleep(2)
            await ctx.guild.voice_client.disconnect()
            await ctx.send("Disconnected.")

    else:
        await ctx.send("Not in VC.")


# Event handler for bot startup
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

bot.run(TOKEN)