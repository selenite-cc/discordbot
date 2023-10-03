import asyncio
from itertools import cycle
import discord
import json
import os
from discord import app_commands


from keep_alive import keep_alive
keep_alive()



token = os.environ['BOT_TOKEN']
server_id = os.environ['SERVER_ID']
lvl_channel = os.environ['LVL_CHANNEL']

intents = discord.Intents.default()
client = discord.Client(intents=intents, activity=discord.CustomActivity(name='🎮 Working on Selenite.'))
tree = app_commands.CommandTree(client)
intents.message_content = True

async def asynclog(data):
    print(data)
    logfile = open('data/log', "a")
    logfile.write(f'\n{data}')
    logfile.close()

def log(data):
    print(data)
    logfile = open('data/log', "a")
    logfile.write(f'\n{data}')
    logfile.close()

users = {}
try:
    with open("data/levels.json") as fp:
        users = json.load(fp)
except Exception:
    pass

def save_users():
    with open("data/levels.json", "w+") as fp:
        json.dump(users, fp, sort_keys=True, indent=4)


async def add_points(user: discord.User):
    id = str(user.id)
    if id not in users:
        users[id] = {"points": 0, "level": 1}
    
    users[id]["points"] += 1
    
    if users[id]["points"] >= 10 * users[id]["level"]:
        users[id]["level"] += 1
        users[id]["points"] = 0
        await send_message(f'{user.name} has leveled up to level {users[id]["level"]}!')
    
    save_users()

async def send_message(message):
    channel = client.get_channel(lvl_channel) # type: ignore
    await channel.send(message) # type: ignore

@client.event
async def on_message_edit(before, after):
    await asynclog(f'Message has been edited by {after.author.name}: {before.content} - {after.content}')

@client.event
async def on_message_delete(message):
    await asynclog(f'Message by {message.author.name} has been deleted: {message.content}')

def get_points(user: discord.User):
    id = str(user.id)
    if id in users:
        return [users[id].get("points", 0), users[id].get("level", 1)]
    return [0, 1]

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    await add_points(message.author)


@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=server_id)) # type: ignore
    await asynclog(f'logged into {client.user}')
    await change_status()

status = cycle(['👨‍💻 Working on Selenite.', '👀 Watching the Selenite Discord', '🎮 Playing on Selenite'])


async def change_status():
  while True:
    await client.change_presence(activity=discord.CustomActivity(next(status)))
    await asyncio.sleep(30)

@tree.command(name = "level", description = "See your level", guild=discord.Object(id=server_id)) # type: ignore
async def send_level(interaction):
    lvls = get_points(interaction.user)
    await interaction.response.send_message(f'You are at level {lvls[1]}, and {lvls[0]}/{10*lvls[1]} points.')


@tree.command(name = "purge", description = "Purge messages", guild=discord.Object(id=server_id)) # type: ignore
async def purge(interaction, amount: int):
    if(interaction.user.guild_permissions.manage_messages == True):
        await interaction.response.send_message(f'Deleted {str(amount)} messages.', ephemeral=True, delete_after=5)
        await interaction.channel.purge(limit=amount)
    else:
        await interaction.response.send_message(f'You need the Manage Messages permission to use this command.', ephemeral=True)

client.run(token) # type: ignore