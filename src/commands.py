from csv import excel
from sqlite3 import IntegrityError
from functools import reduce
from typing import List, Optional
import discord
from typing import cast
from discord import app_commands

from src.custom_elements import ProjectSelect, CreateTaskModal, DUPLICATED_PKEY, list_task_for_project_name
from src.domain.entities import *
from src.utils import DiscordEmbdeddingFac
from peewee import IntegrityError, DoesNotExist


FOREIGN_KEY_VIOLATION = 'FOREIGN KEY constraint failed'


@app_commands.command(name='show-todo')
async def show(interaction: discord.Interaction):
    response = cast(discord.InteractionResponse, interaction.response)

    embded = discord.Embed(
        description="""
-**add-task** project-name task_name
-**edit-task** project-name task_num
-**complete-task** project-name task_num
-**list-tasks** {project-name | username}
-**drop-assigment** project-name task_num 
-**take-on** project-name task_num 
-**assign** project-name task_num username 
-**add-project** project-name
-**remove-project** project-name
"""
        ,
        color=discord.Color.dark_gray(),
        title='**Available Commands**'
    )

    await response.send_message(embed=embded)


def list_projects(server_name: str,cached: List[Project]|None = None ) -> str:
    projects: List[Project] | None = cached if cached is not None else Project.select().where(Project.server_name == server_name)
    if projects is None or len(projects) == 0:
        return "No projects found"
    return reduce(
        lambda acc, next: acc + '\n' + next,
        map(lambda pr: '-' + pr.name, projects),
    )



async def check_if_project_exist(interaction: discord.Interaction, project_name: str, projects:List[Project]):
    filtered=[p for p in projects if p.name == project_name]
    if len(filtered) == 0:
        await interaction.response.send_message(
            embed=DiscordEmbdeddingFac.create_error_message(
                body="The project doesn't exists, here are the available project:\n" + list_projects(
                    interaction.guild.name)
            )
        )
        raise ValueError()

async def check_tasks(tasks:List[Task], interaction: discord.Interaction,task_num):
    if task_num < 0:
        await interaction.response.send_message(
            embed=DiscordEmbdeddingFac.create_error_message(
                body="Only positive numbers for task_num are allowed"
            )
        )
        raise ValueError()

    elif len(tasks) <= task_num - 1:
        await interaction.response.send_message(
            embed=DiscordEmbdeddingFac.create_error_message(
                body=f"The task number is out of range"
            )
        )
        raise ValueError()




@app_commands.command(name='add-project',description="Creates a new project, if there isn't one with the same name")
@app_commands.describe(project_name='The name of the project you want to add')
async def bot_add_project(interaction: discord.Interaction,
                          project_name: str):
    try:
        Project.create(name=project_name, server_name=interaction.guild.name)
        await interaction.response.send_message(
            embed=DiscordEmbdeddingFac.create_simple_dark_bg(
                title='Projects:',
                body=list_projects(interaction.guild.name)
            ))
    except IntegrityError as e:
        if DUPLICATED_PKEY in str(e):
            await interaction.response.send_message(embed=DiscordEmbdeddingFac.create_error_message(
                body=f'There already exists a project with the name {project_name}'))


@app_commands.command(name='list-projects')
async def bot_list_projects(interaction: discord.Interaction):
    await interaction.response.send_message(
        embed=DiscordEmbdeddingFac.create_simple_dark_bg(title='Projects:', body=list_projects(interaction.guild.name)))


@app_commands.command(name='remove-project',description="Removes a given project")
@app_commands.describe(project_name='The name of the project you want to remove')
async def bot_remove_project(interaction: discord.Interaction,project_name: str):
    try:
        projects=Project.get_for_server_name(interaction.guild.name)
        await check_if_project_exist(interaction, project_name, projects)

        Project.delete().where(
            (Project.name == project_name) & (Project.server_name == interaction.guild.name)
        ).execute()

        projects=[p for p in projects if p.name != project_name]

        await interaction.response.send_message(embed=DiscordEmbdeddingFac.create_simple_dark_bg(
            title='Projects',
            body=list_projects(interaction.guild.name,cached=projects)
        ))
    except ValueError:
        pass


@app_commands.command(name="list-tasks",description="Shows the tasks registered to a given project")
async def bot_list_tasks(interaction: discord.Interaction,project_name: str):
    try:
        projects=Project.get_for_server_name(interaction.guild.name)
        await check_if_project_exist(interaction, project_name,projects)

        await interaction.response.send_message(
            embed=DiscordEmbdeddingFac.create_simple_dark_bg(
                title=f"Project[{project_name}] tasks:",
                body=list_task_for_project_name(interaction.guild.name, project_name)
            )
        )
    except ValueError:
        pass

@app_commands.command(name='add-task',description="Create a new task")
async def bot_add_task(interaction: discord.Interaction,project_name: str):
    try:
        projects=Project.get_for_server_name(interaction.guild.name)
        await check_if_project_exist(interaction, project_name, projects)
        await interaction.response.send_modal(
            CreateTaskModal(project_name=project_name)
        )
    except ValueError:
        pass

@app_commands.command(name='mark-completed',description="Marks a task as completed and removes it")
@app_commands.describe(project_name="The name of the project to which the task belongs",task_num="The order of the task that you completed")
async def bot_mark_task_as_completed(interaction: discord.Interaction,project_name: str,task_num: int):
    try:
        projects=Project.get_for_server_name(interaction.guild.name)
        await check_if_project_exist(interaction, project_name,projects)

        tasks=Task.get_tasks_for_project(server_name=interaction.guild.name, project_name=project_name)
        await check_tasks(tasks=tasks, interaction=interaction, task_num=task_num)

        task_num-=1
        tasks[task_num].delete_instance()
        tasks=[t for i,t in enumerate(tasks) if i!=task_num]

        await interaction.response.send_message(
            embed=DiscordEmbdeddingFac.create_simple_dark_bg(
                title=f"Project[{project_name}] tasks:",
                body=list_task_for_project_name(server_name=interaction.guild.name,
                                                project_name=project_name,cached=tasks)
            )
        )
    except ValueError:
        pass


@app_commands.command(name='edit-task',description="Edits a given task")
@app_commands.describe(project_name='The name of the project to which the task belongs',task_num="The order of the task that you want edited")
async def bot_edit_task(interaction: discord.Interaction,project_name: str,task_num: int,new_task_name: str ):
    try:
        projects=Project.get_for_server_name(interaction.guild.name)
        await check_if_project_exist(interaction, project_name,projects)

        tasks = Task.get_tasks_for_project(server_name=interaction.guild.name, project_name=project_name)
        await check_tasks(tasks=tasks, interaction=interaction, task_num=task_num)

        new_task_name = new_task_name.strip()
        if not new_task_name:
            await interaction.response.send_message(
                embed=DiscordEmbdeddingFac.create_error_message(
                    body="Empty task name"
                )
            )
            return

        task_num-=1

        Task.update(name=new_task_name).where(
            (Task.name==tasks[task_num].name) & (Task.server_name == tasks[task_num].server_name) & \
            (Task.project_name==tasks[task_num].project_name)
        ).execute()
        tasks[task_num].name=new_task_name

        await interaction.response.send_message(
            embed=DiscordEmbdeddingFac.create_simple_dark_bg(
                title=f"Project[{project_name}] tasks:",
                body=list_task_for_project_name(server_name=interaction.guild.name,
                                                project_name=project_name,cached=tasks)
            )
        )
    except IntegrityError as e :
        if DUPLICATED_PKEY in e:
            await interaction.response.send_message(DiscordEmbdeddingFac.create_error_message(
                body=f"The task name already exists"
            ))
    except ValueError:
        pass


@app_commands.command(name='assign',description="Assigns a given project to a user")
@app_commands.describe(project_name='The name of the project you want to assign',task_num='The task number you want to assign to the user with the username provided ')
async def bot_assign_task(interaction: discord.Interaction,project_name: str,task_num: int,member: discord.Member):
    try:
        projects=Project.get_for_server_name(interaction.guild.name)
        await check_if_project_exist(interaction, project_name,projects)

        tasks=Task.get_tasks_for_project(server_name=interaction.guild.name, project_name=project_name)
        await check_tasks(tasks, interaction,task_num)

        task_num-=1

        Task.update({Task.assignee_username : member.name}).where(
            (Task.project_name == project_name) & (Task.server_name == interaction.guild.name) &
            (Task.name == tasks[task_num].name)
        ).execute()

        tasks[task_num].assignee_username=member.name

        await interaction.response.send_message(
            embed=DiscordEmbdeddingFac.create_simple_dark_bg(
                title=f"Project[{project_name}] tasks:",
                body=list_task_for_project_name(server_name=interaction.guild.name,project_name=project_name,
                                                cached=tasks)
            )
        )
    except ValueError:
        pass

