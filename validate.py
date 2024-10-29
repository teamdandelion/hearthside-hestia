import discord
from dotenv import load_dotenv
import os

load_dotenv()
client = discord.Client(intents=discord.Intents.default())

@client.event
async def on_ready():
    print(f'Successfully logged in as {client.user}')
    await client.close()

client.run(os.getenv('DISCORD_TOKEN'))
