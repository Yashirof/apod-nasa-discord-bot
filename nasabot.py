import discord
from discord.ext import commands, tasks
import requests
import asyncio

intents = discord.Intents.default()
intents.typing = False
intents.presences = False

bot_token = 'yourtoken'
nasa_api_key = 'your_nasa_api_key'
channel_id = your_channel_id

bot = commands.Bot(command_prefix='!', intents=intents, case_insensitive=True)

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user.name}')
    await send_apod_daily.start()

@tasks.loop(hours=24)
async def send_apod_daily():
    await asyncio.sleep(5)  
    channel = bot.get_channel(channel_id)
    await send_apod(channel)

@bot.event
async def on_message(message):
    if message.content.startswith('!apod'):
        channel = bot.get_channel(channel_id)
        await send_apod(channel)
    await bot.process_commands(message)

async def send_apod(channel):
    response = requests.get(f'https://api.nasa.gov/planetary/apod?api_key={nasa_api_key}')

    if response.status_code == 200:
        data = response.json()
        title = data['title']
        image_url = data['url']
        explanation = data['explanation']

        await channel.send(f'**{title}**\n{explanation}\n{image_url}')
    else:
        print('Erro ao obter a foto do APOD')

bot.run(bot_token)
