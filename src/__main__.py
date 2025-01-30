import discord

intents=discord.Intents(
    message_content=True,
)
client=discord.Client(intents=intents)
# client.connect(,reconnect=True)