from discord import Intents
from dotenv import load_dotenv
from .TodoBotClient import TodoBotClient
import os

load_dotenv()
bot_token: str | None = os.getenv("BOT_TOKEN")

if bot_token is None:
    print("Bot token identification not provided")
    exit(1)


intent=Intents(message_content=True)
client=TodoBotClient(intents=intent)
client.run(bot_token)