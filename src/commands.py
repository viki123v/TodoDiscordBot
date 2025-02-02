from sqlite3 import IntegrityError
from functools import reduce
from typing import List, Optional
import discord
from typing import cast
from discord import app_commands

from src.custom_elements import ProjectSelect, CreateTaskModal, DUPLICATED_PKEY, list_task_for_project_name
from src.domain.entities import *
from src.embdedding_fac import DiscordEmbdeddingFac
from peewee import IntegrityError, DoesNotExist

"""
So projki da ti izlegvat taskojte  
"""

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


def list_projects(server_name: str) -> str:
    projects: List[Project] | None = Project.select().where(Project.server_name == server_name)
    if projects is None or len(projects) == 0:
        return "No projects found"
    return reduce(
        lambda acc, next: acc + '\n' + next,
        map(lambda pr: '-' + pr.name, projects),
    )


@app_commands.command(name='add-project',
                      description="Creates a new project, if there isn't one with the same name")
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


@app_commands.command(name='remove-project',
                      description="Removes a given project")
@app_commands.describe(project_name='The name of the project you want to remove')
async def bot_remove_project(interaction: discord.Interaction,
                             project_name: str):
    try:
        Project.delete().where(
            (Project.name == project_name) & (Project.server_name == interaction.guild.name)
        ).execute()
        await interaction.response.send_message(embed=DiscordEmbdeddingFac.create_simple_dark_bg(
            title='Projects',
            body=list_projects(interaction.guild.name)
        ))
    except DoesNotExist:
        interaction.response.send_message(
            embed=DiscordEmbdeddingFac.create_error_message(body=f"The project {project_name} doesn't exist")
        )


@app_commands.command(name="list-tasks",
                      description="Shows the tasks registered to a given project")
async def bot_list_tasks(interaction: discord.Interaction,
                         project_name: str):
    await interaction.response.send_message(
        embed=DiscordEmbdeddingFac.create_simple_dark_bg(
            title=f"Project[{project_name}] tasks:",
            body=list_task_for_project_name(interaction.guild.name, project_name)
        )
    )


async def check_if_project_exist(interaction: discord.Interaction, project_name: str):
    if len(Project.select().where(
            (Project.name == project_name) & (Project.server_name == interaction.guild.name))) == 0:
        await interaction.response.send_message(
            embed=DiscordEmbdeddingFac.create_error_message(
                body="The project doesn't exists, here are the available project:\n" + list_projects(
                    interaction.guild.name)
            )
        )
        return False
    return True

async def check_tasks(tasks:List[Task], interaction: discord.Interaction,task_num):
    if task_num < 0:
        await interaction.response.send_message(
            embed=DiscordEmbdeddingFac.create_error_message(
                body="Only positive numbers for task_num are allowed"
            )
        )
        return False
    elif len(tasks) <= task_num - 1:
        await interaction.response.send_message(
            embed=DiscordEmbdeddingFac.create_error_message(
                body=f"The task number is out of range"
            )
        )
        return False

    return True

@app_commands.command(name='add-task',
                      description="Create a new task")
async def bot_add_task(interaction: discord.Interaction,
                       project_name: str):
    exists = await check_if_project_exist(interaction, project_name)
    if not exists:
        return
    await interaction.response.send_modal(
        CreateTaskModal(project_name=project_name)
    )



@app_commands.command(name='mark-completed',
                      description="Marks a task as completed and removes it")
@app_commands.describe(project_name="The name of the project to which the task belongs",
                       task_num="The order of the task that you completed")
async def bot_mark_task_as_completed(interaction: discord.Interaction,
                                     project_name: str,
                                     task_num: int):
    exists = await check_if_project_exist(interaction, project_name)

    if not exists:
        return

    tasks=Task.get_tasks_for_project(server_name=interaction.guild.name, project_name=project_name).order_by(Task.name)
    task_ok = check_tasks(tasks=tasks, interaction=interaction, task_num=task_num)

    if not task_ok:
        return

    for_deletion = tasks[task_num - 1]
    for_deletion.delete_instance()

    await interaction.response.send_message(
        embed=DiscordEmbdeddingFac.create_simple_dark_bg(
            title=f"Project[{project_name}] tasks:",
            body=list_task_for_project_name(server_name=interaction.guild.name,
                                            project_name=project_name)
        )
    )


@app_commands.command(name='edit-task',
                      description="Edits a given task")
@app_commands.describe(project_name='The name of the project to which the task belongs',
                       task_num="The order of the task that you want edited")
async def bot_edit_task(interaction: discord.Interaction,
                        project_name: str,
                        task_num: int,
                        new_task_name: str ):
    proejcts_ok =check_if_project_exist(interaction, project_name)

    if not proejcts_ok:
        return

    tasks = Task.get_tasks_for_project(server_name=interaction.guild.name, project_name=project_name).order_by(
        Task.name)
    tasks_ok=check_tasks(tasks=tasks, interaction=interaction, task_num=task_num)

    if not tasks_ok:
        return

    if new_task_name in set([t.name for t in tasks]):
        await interaction.response.send_message(
            embed=DiscordEmbdeddingFac.create_error_message(
                body=f"The task name already exists"
            )
        )
        return

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
        (Task.name==tasks[task_num].name) & (Task.server_name == tasks[task_num].server_name)
    ).execute()

    await interaction.response.send_message(
        embed=DiscordEmbdeddingFac.create_simple_dark_bg(
            title=f"Project[{project_name}] tasks:",
            body=list_task_for_project_name(server_name=interaction.guild.name,
                                            project_name=project_name)
        )
    )


@app_commands.command(name='drop-assigment',
                      description="Unassigns a given task")
@app_commands.describe(project_name='The name of the project, in which the task belongs',
                       task_num='The task number you want to drop assigment')
async def bot_drop_assigment(interaction: discord.Interaction,
                             project_name: str,
                             task_num: int):
    pass


@app_commands.command(name='assign',
                      description="Assigns a given project to a user")
@app_commands.describe(project_name='The name of the project you want to assign',
                       task_num='The task number you want to assign to the user with the username provided ',
                       username="The username of the user, you want to assign to this task")
async def bot_assign_task(interaction: discord.Interaction,
                          project_name: str,
                          task_num: int,
                          username: str):
    pass


@app_commands.command(name='take-on',
                      description="Assign to your self a task from a given project")
@app_commands.describe(project_name='The name of the project you want take',
                       task_num='The task number you want to take up on ', )
async def bot_take_on_task(interaction: discord.Interaction,
                           project_name: str,
                           task_num: int):
    pass
