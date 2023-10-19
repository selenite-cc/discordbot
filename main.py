import asyncio
from itertools import cycle
from typing import Optional
import discord
import json
import os
from discord import app_commands
from dotenv import load_dotenv
import time
from profanity_check import predict
import re

load_dotenv()



from keep_alive import keep_alive
keep_alive()

swears = open("filterlist", "r")
swears = swears.read().split('\n')
specialchars = [*"'/.,<>[]=-`#%^&*()\""]
replace = re.findall('..', "1i3e4a0o@a!i$svu")



token = os.environ['BOT_TOKEN']
server_id = os.environ['SERVER_ID']
lvl_channel = int(os.environ['LVL_CHANNEL'])
widgets = os.environ['WIDGETS']
logs = os.environ['LOGS']

intents = discord.Intents.default()
client = discord.Client(intents=intents, activity=discord.CustomActivity(name='🎮 Working on Selenite.'), allowed_mentions=discord.AllowedMentions(roles=False, users=False, everyone=False))
tree = app_commands.CommandTree(client)
intents.message_content = True

async def log(data):
    print(data)
    logfile = open('data/log', "a")
    logfile.write(f'\n{data}')
    logfile.close()
    channel = client.get_channel(int(logs))
    await channel.send(data) # type: ignore


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
        users[id] = {"points": 0, "level": 1, "lastmsg" : int(time.time())}
    if users[id]["lastmsg"] + 10 <= int(time.time()):
        users[id]["points"] += 1
        users[id]["lastmsg"] = int(time.time())
    
    if users[id]["points"] >= 10 * users[id]["level"]:
        users[id]["level"] += 1
        users[id]["points"] = 0
        channel = client.get_channel(lvl_channel)
        await channel.send(f'{user.name} has leveled up to level {users[id]["level"]}!') # type: ignore
        await checkRewards(user, users[id]["level"])
      
    save_users()

async def checkRewards(user: discord.User, level: int):
    return None # currently no rewards

@client.event
async def on_message_edit(before, after):
    await log(f'Message has been edited by {after.author.name}: {before.content} - {after.content}')

@client.event
async def on_message_delete(message):
    await log(f'Message by {message.author.name} has been deleted: {message.content}')

def get_points(user: discord.User):
    id = str(user.id)
    if id in users:
        return [users[id].get("points", 0), users[id].get("level", 1)]
    return [0, 1]

@client.event
async def on_message(message):
    if message.author.id == 1158146828592754851:
        return
    if int(message.channel.id) == int(widgets):
        usrmsg = message.content
        for repl in replace:
            usrmsg = usrmsg.replace(repl[0], repl[1])
        for char in specialchars:
            usrmsg = usrmsg.replace(char, "")
        filter = predict([usrmsg])
        usrmsg = usrmsg.split(' ')
        for word in usrmsg:
            if word in swears:
                await message.delete()
                await message.channel.send(f'{message.author}\'s message was deleted.')
                return
        if filter >= 0.9:
            await message.delete()
            await message.channel.send(f'{message.author}\'s message was deleted.')
    if message.author.bot or message.webhook_id:
        return
    await add_points(message.author)


@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=server_id)) # type: ignore
    logfile = open('data/log', "a")
    logfile.write(f'\n\n\n\nBot has started. Logged in as {client.user}\n\n\n\n')
    logfile.close()
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
        await log(f'Purged {str(amount)} messages, initiated by {interaction.user.name}')
    else:
        await interaction.response.send_message(f'You need the Manage Messages permission to use this command.', ephemeral=True)

@tree.command(name = "setlevel", description = "Set a user's level", guild=discord.Object(id=server_id)) # type: ignore
async def setlevel(interaction, user: discord.User, level: int, points: Optional[int]):
    if(interaction.user.guild_permissions.administrator == True):
        if points is None:
            points = 0
        id = str(user.id)
        users[id]["level"] = int(level)
        users[id]["points"] = int(points)
        await interaction.response.send_message(f"Set {user.name}'s level to level {level}, and set their points to {points}.", ephemeral=True)
        save_users()
        await log(f"Set {user.name}'s level to level {level}, and set their points to {points}.")
    else:
        await interaction.response.send_message(f'You need the Administrator permission to use this command.', ephemeral=True)

@tree.command(name = "echo", description = "Repeat your input", guild=discord.Object(id=server_id)) # type: ignore
async def echo(interaction, text: str):
    channel = client.get_channel(interaction.channel_id)
    await channel.send(text) # type: ignore
    await interaction.response.send_message(f'Sending message.', ephemeral=True)

client.run(token) # type: ignore