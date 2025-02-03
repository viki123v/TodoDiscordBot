from discord import Embed,Color


class DiscordEmbdeddingFac:
    @staticmethod
    def create_simple_dark_bg(body:str, title:str):
        return Embed(title=title, description=body,colour=Color.dark_gray())

    @staticmethod
    def create_error_message(body:str):
        return Embed(title='**ERROR**',description=body,colour=Color.red())


