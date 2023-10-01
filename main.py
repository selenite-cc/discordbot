# This example requires the 'message_content' intent.

import discord
import os
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()

token = os.getenv('BOT_TOKEN')

intents = discord.Intents.default()
client = discord.Client(intents=intents, activity=discord.CustomActivity(name='🎮 Working on Selenite.'))
tree = app_commands.CommandTree(client)
intents.message_content = True

@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=1158146475327488001))
    print(f'logged into {client.user}')

@tree.command(name = "embed", description = "Create an embed", guild=discord.Object(id=1158146475327488001))
async def send_embed(interaction, title: str, description: str, color: str):
    embed=discord.Embed(title=title, description=description, color=discord.Colour.from_str("#" + color))
    await interaction.response.send_message(embed=embed)

client.run(token)
