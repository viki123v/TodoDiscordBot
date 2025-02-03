from discord.ext.commands import Bot
import discord
from peewee import IntegrityError
from .embdedding_fac import DiscordEmbdeddingFac
from .domain.entities import Project, Task
from typing import List

DUPLICATED_PKEY = 'duplicate key value'


def list_task_for_project_name(server_name: str, project_name: str ) -> str:
    tasks: List[Task] | None = Task.select().where(
        (Task.server_name == server_name) & (Task.project_name == project_name)
    ).order_by(Task.name)
    if tasks is None or len(tasks) == 0:
        return "No tasks found"
    return '\n'.join(
        map(lambda t: str(t[0]) + '. ' + t[1].name, enumerate(tasks))
    )


class TodoBotClient(Bot):
    def __init__(self, intents, application_id, command_prefix):
        super().__init__(intents=intents,
                         application_id=application_id,
                         command_prefix=command_prefix)
        self._projects = {}

    async def on_ready(self):
        await self.tree.sync()

    async def on_message(self, message):
        if message.author == self.user:
            return
        await self.process_commands(message)


class ProjectSelect(discord.ui.Select):
    def __init__(self, server_name: str):
        super().__init__(
            options=[
                discord.SelectOption(value=p.name, label=p.name)
                for p in Project.select().where(Project.server_name == server_name)
            ],
        )


class CreateTaskModal(discord.ui.Modal):

    def __init__(self, project_name: str):
        super().__init__(title='Create new tasks')
        self.project_name = project_name
        self.task_name_ui = discord.ui.TextInput(
            required=True,
            label="Enter new your new tasks name here",
            placeholder="For multiple tasks use \",\"",
            max_length=500,
            min_length=1,
        )
        self.add_item(self.task_name_ui)


    async def on_submit(self, interaction: discord.Interaction):
        task_names = self.task_name_ui.value.split(',')
        duplicated: List[str] =[]

        for task_name in task_names:

            task_name=task_name.strip()

            if not task_name:
                continue

            try:
                Task.create(name=task_name,
                            server_name=interaction.guild.name,
                            project_name=self.project_name)
            except IntegrityError as e:
                if DUPLICATED_PKEY in str(e):
                    duplicated.append(task_name)
                    continue
                raise e

        await interaction.response.send_message(
            embed=DiscordEmbdeddingFac.create_error_message(
                body=f'The tasks [{", ".join(duplicated)}] already exists.',
            )
        )

        await interaction.followup.send(
            embed=DiscordEmbdeddingFac.create_simple_dark_bg(
                title=f'Project[{self.project_name}] tasks:',
                body=list_task_for_project_name(server_name=interaction.guild.name,project_name=self.project_name)
            )
        )
