import peewee
from discord import Embed,Color
from typing import List,Type
import discord

from src.domain.entities import Project,Task


class DiscordEmbdeddingFac:
    @staticmethod
    def create_simple_dark_bg(body:str, title:str):
        return Embed(title=title, description=body,colour=Color.dark_gray())

    @staticmethod
    def create_error_message(body:str):
        return Embed(title='**ERROR**',description=body,colour=Color.red())

class Cache:
    def __init__(self):
        self.result: List[peewee.Model]| None = None
        self.last : List[Project] | None = None

    def clean(self):
        self.result = None



class ProjectCache(Cache):
    _instance=None

    def __init__(self):
        super().__init__()
        self.last : List[Project]|None=None
        self.projects_for_server : List[Project]|None=None

    def filter(self, server_name: str|None , current_name: str|None) -> List[Project]:
        if server_name is None:
            return []

        self.last = None

        if self.projects_for_server is None:
            self.projects_for_server = list(Project.select().where(Project.server_name == server_name).order_by(Project.name))

        if current_name is None or not current_name.strip():
            self.last = self.projects_for_server
        else:
            current_name= current_name.strip()
            self.last : List[Project] = [pr for pr in self.projects_for_server if pr.name.startswith(current_name)]

        return self.last

    async def filter_commands(self, interaction: discord.Interaction, project_name:str|None):
        last : List[Project] = self.filter(interaction.guild.name, project_name)
        return [
            discord.app_commands.Choice(name=pr.name, value=pr.name)
            for pr in last
        ]

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def clean(self):
        super().clean()
        self.last = None
        self.projects_for_server = None

class TaskCache(Cache):
    _instance=None

    def __init__(self):
        super().__init__()
        self.last: List[Task] | None = None
        self.tasks_for_server_and_project: List[Task] | None = None

    async def filter(self, server_name: str|None, project_name:str|None, task_name:str|None ) -> List[discord.app_commands.Choice]:
        if server_name is None or project_name is None:
            return []

        self.last = None

        if self.tasks_for_server_and_project is None:
            self.result = list(Task.select().where(Task.server_name == server_name) & (Task.project_name == project_name))

        if task_name is None or not task_name.strip():
            self.last = self.tasks_for_server_and_project
        else:
            current_name= task_name.strip()
            self.last = [t for t in self.result if t.name.startswith(current_name)]

        return [
            discord.app_commands.Choice(name=t.name, value=t.name)
            for t in self.last
        ]

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance


    def clean(self):
        super().clean()
        self.last=None
        self.tasks_for_server_and_project=None

async def check_if_query_empty(interaction:discord.Interaction,cache: ProjectCache):
    if cache.last is None or len(cache.last) != 1 :
        await interaction.response.send_message(embed=DiscordEmbdeddingFac.create_error_message(body="Please check you selection"))
        raise ValueError("Not selected")


