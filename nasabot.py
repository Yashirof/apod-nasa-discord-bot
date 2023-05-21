import discord
from discord.ext import commands, tasks
import asyncio
import aiohttp

intents = discord.Intents.default()
intents.typing = False
intents.presences = False

# definir isso em variável de ambiente para melhor qualidade de código:
bot_token = 'seu_bot_token'
nasa_api_key = 'sua_nasa_api_key'


bot = commands.Bot(command_prefix='!', intents=intents, case_insensitive=True)

# Faz a requisição de maneira assíncrona
async def get_apod():
    # Define URL da request
    url = f'https://api.nasa.gov/planetary/apod?api_key={nasa_api_key}'

    # Instancia uma sessão async
    async with aiohttp.ClientSession() as session:

        # faz a requisição de maneira async
        async with session.get(url) as response:

            # Verifica o status da request
            if response.status == 200:
                res = await response.json()

                # Gera um json apenas com os dados desejados (para facilitar leitura posteriormente)
                json = {
                    'title': res['title'],
                    'image_url': res['url'],
                    'explanation': res['explanation']
                }
                return json
            else:
                print('Erro ao obter a foto do APOD')


class Apod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    # Define que o nome do comando será "apod" (basta dar !apod para que ele seja invocado)
    @commands.command(name='apod', description='sends apod')
    async def send_apod(self, ctx):
        try:
            apod = await get_apod()

            await ctx.channel.send(f"**{apod['title']}**\n{apod['explanation']}\n{apod['image_url']}")
        except Exception as E:
            print(E)
            ctx.send(f"Erro na função apod: {E}")


@tasks.loop(hours=24)
async def apod_daily():
    """Roda 1 vez ao dia"""
    await asyncio.sleep(5)
    for guild in bot.guilds:
        # Se o servidor tiver um canal de "system channel",
        # esse será o canal onde o apod será enviado por padrão
        if guild.system_channel:
            apod = await get_apod()

            await guild.system_channel.send(f"**{apod['title']}**\n{apod['explanation']}\n{apod['image_url']}")


@bot.event
async def on_ready():
    """Quando bot estiver pronto..."""
    print("===============================================")
    print('Entrei como', bot.user)
    print(f"Nome: {bot.user.name} | ID: {bot.user.id}")
    print("===============================================")

    await apod_daily.start()


@bot.event
async def on_message(message):
    """For each received message"""

    # para que o bot não responda a si mesmo
    if message.author.id == bot.user.id:
        return

    # Loga todas as mensagens enviadas no chat
    print(f"recebi uma mensagem em {message.guild.name} | Enviada por {message.author}: {str(message.content)}")

    await bot.process_commands(message)


@bot.event
async def on_member_join(member):
    guild = member.guild
    try:
        print(f"Membro novo em {guild.name}")

        # caso o servidor tenho um "system channel", dará boas-vindas
        # aos novos membros
        if guild.system_channel is not None:
            mensagem = f"Bem vindo {member.mention} ao {guild.name}!!!"
            await asyncio.sleep(1)
            await guild.system_channel.send(mensagem)

    except Exception as E:
        print("Exceção 01 em on_member_join: " + str(E))


if __name__ == "__main__":
    bot.add_cog(Apod(bot=bot))
    bot.run(bot_token)
