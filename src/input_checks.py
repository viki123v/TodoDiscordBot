import discord
from src.domain.entities import Project,Task
from src.utils import DiscordEmbdeddingFac
from src.custom_elements import list_projects
from typing import List

# async def check_if_project_exist(interaction: discord.Interaction, project_name: str):
#     if len(Project.select().where(
#             (Project.name == project_name) & (Project.server_name == interaction.guild.name))) == 0:
#         await interaction.response.send_message(
#             embed=DiscordEmbdeddingFac.create_error_message(
#                 body="The project doesn't exists, here are the available project:\n" + list_projects(
#                     interaction.guild.name)
#             )
#         )
#         raise ValueError('The project doesn\'t exists')

async def check_tasks_num(tasks:List[Task], interaction: discord.Interaction,task_num):
    err=ValueError('Error')
    if task_num < 0:
        await interaction.response.send_message(
            embed=DiscordEmbdeddingFac.create_error_message(
                body="Only positive numbers for task_num are allowed"
            )
        )
        raise err
    elif len(tasks) <= task_num - 1:
        await interaction.response.send_message(
            embed=DiscordEmbdeddingFac.create_error_message(
                body=f"The task number is out of range"
            )
        )
        raise err

async def is_empty_new_task_name(interaction:discord.Interaction, new_task_name:str):
    if not new_task_name:
        await interaction.response.send_message(
            embed=DiscordEmbdeddingFac.create_error_message(
                body="Empty task name"
            )
        )
        raise ValueError('Empty task name')
