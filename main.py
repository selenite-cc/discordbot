# This example requires the 'message_content' intent.

import discord
import json
import os
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()

token = os.getenv('BOT_TOKEN')
server_id = 1158146475327488001
lvl_channel = 1158146475897917453

intents = discord.Intents.default()
client = discord.Client(intents=intents, activity=discord.CustomActivity(name='🎮 Working on Selenite.'))
tree = app_commands.CommandTree(client)
intents.message_content = True


users = {}  # Initialize users as an empty dictionary
try:
    with open("data/levels.json") as fp:
        users = json.load(fp)
except Exception:
    pass

def save_users():
    with open("data/levels.json", "w+") as fp:
        json.dump(users, fp, sort_keys=True, indent=4)


def add_points(user: discord.User, users_dict):
    id = str(user.id)
    if id not in users_dict:
        users_dict[id] = {"points": 0, "level": 1}
    
    users_dict[id]["points"] += 1
    
    if users_dict[id]["points"] >= 10 * users_dict[id]["level"]:
        users_dict[id]["level"] += 1
        users_dict[id]["points"] = 0
    
    print("{} now has {} points".format(user.name, users_dict[id]["points"]))
    print("{} is at level {}".format(user.name, users_dict[id]["level"]))
    
    save_users()


def get_points(user: discord.User):
    id = str(user.id)
    print(id)
    if id in users:
        print("found user in level")
        return [users[id].get("points", 0), users[id].get("level", 1)]
    return [0, 1]

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    print("{} sent a message".format(message.author.name))
    add_points(message.author, users)


@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=server_id))
    print(f'logged into {client.user}')

@tree.command(name = "embed", description = "Create an embed", guild=discord.Object(id=server_id))
async def send_embed(interaction, title: str, description: str, color: str):
    embed=discord.Embed(title=title, description=description, color=discord.Colour.from_str("#" + color))
    await interaction.response.send_message(embed=embed)

@tree.command(name = "level", description = "See your level", guild=discord.Object(id=server_id))
async def send_level(interaction):
    lvls = get_points(interaction.user)
    await interaction.response.send_message(f'You are at level {lvls[1]}, and {lvls[0]}/{10*lvls[1]} points.')

client.run(token)
