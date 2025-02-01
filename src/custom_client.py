from discord.ext.commands import Bot

class TodoBotClient(Bot):
    def __init__(self,intents,application_id,command_prefix):
        super().__init__(intents=intents,
                         application_id=application_id,
                         command_prefix=command_prefix)
        self._projects={}

    async def on_ready(self):
        await self.tree.sync()

    async def on_message(self,message):
        if message.author == self.user:
            return
        await self.process_commands(message)