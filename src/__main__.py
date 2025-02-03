import discord
import inspect
from dotenv import load_dotenv
from . import custom_elements,commands
from . import domain


import os

load_dotenv()

bot_token: str = os.getenv("BOT_TOKEN")
app_id: int = int(os.getenv("APPLICATION_ID"))

intent = discord.Intents.default()
intent.message_content = True
intent.members = True

client = custom_elements.TodoBotClient(intents=intent,application_id=app_id,command_prefix='/')

for mem in inspect.getmembers(commands):
    name,obj=mem
    if name.startswith('bot_') and isinstance(obj,discord.app_commands.Command):
        client.tree.add_command(obj)

client.run(bot_token)