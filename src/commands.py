from sqlite3 import IntegrityError
import discord
from typing import cast
from discord import app_commands
from src.custom_elements import  CreateTaskModal, DUPLICATED_PKEY, list_task_for_project_name, list_projects
from src.domain.entities import *
from src.embdedding_fac import DiscordEmbdeddingFac
from peewee import IntegrityError, DoesNotExist
from src.input_checks import *

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


@app_commands.command(name='add-project',description="Creates a new project, if there isn't one with the same name")
@app_commands.describe(project_name='The name of the project you want to add')
async def bot_add_project(interaction: discord.Interaction,project_name: str):
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
        embed=DiscordEmbdeddingFac.create_simple_dark_bg(title='Projects:', body=list_projects(interaction.guild.name))
    )


@app_commands.command(name='remove-project',description="Removes a given project")
@app_commands.describe(project_name='The name of the project you want to remove')
async def bot_remove_project(interaction: discord.Interaction, project_name: str):
    try:
        projects:List[Project]=Project.select().where(Project.server_name == interaction.guild.name)

        filtered=[]
        for project in projects:
            if project.name == project_name:
                Project.delete().where((Project.name==project.name) & (Project.server_name==project.server_name)).execute()
            else:
                filtered.append(project)

        await interaction.response.send_message(embed=DiscordEmbdeddingFac.create_simple_dark_bg(
            title='Projects',
            body=list_projects(interaction.guild.name,cached=filtered)
        ))
    except DoesNotExist:
        interaction.response.send_message(
            embed=DiscordEmbdeddingFac.create_error_message(body=f"The project {project_name} doesn't exist")
        )


@app_commands.command(name="list-tasks",description="Shows the tasks registered to a given project")
async def bot_list_tasks(interaction: discord.Interaction, project_name: str):
    await interaction.response.send_message(
        embed=DiscordEmbdeddingFac.create_simple_dark_bg(
            title=f"Project[{project_name}] tasks:",
            body=list_task_for_project_name(interaction.guild.name, project_name)
        )
    )

@app_commands.command(name='add-task',description="Create a new task")
async def bot_add_task(interaction: discord.Interaction,project_name: str):
    try:
        await check_if_project_exist(interaction, project_name)
        await interaction.response.send_modal(
            CreateTaskModal(project_name=project_name)
        )
    except ValueError as e:
        print(str(e))


@app_commands.command(name='mark-completed',description="Marks a task as completed and removes it")
@app_commands.describe(project_name="The name of the project to which the task belongs",task_num="The order of the task that you completed")
async def bot_mark_task_as_completed(interaction: discord.Interaction,project_name: str,task_num: int):
    try:
        await check_if_project_exist(interaction, project_name)

        tasks:List[Task] = Task.get_tasks_for_project_ordered(server_name=interaction.guild.name, project_name=project_name)

        await check_tasks_num(tasks=tasks, interaction=interaction, task_num=task_num)

        task_num-=1
        selected:Task=tasks[task_num]
        Task.delete().where((Task.server_name==selected.server_name) & (Task.name==selected.name) & \
                            (Task.project_name==selected.project_name)).execute()


        await interaction.response.send_message(
            embed=DiscordEmbdeddingFac.create_simple_dark_bg(
                title=f"Project[{project_name}] tasks:",
                body=list_task_for_project_name(server_name=interaction.guild.name,project_name=project_name,cached=[t for i,t in enumerate(tasks) if i!=task_num])
            )
        )
    except ValueError as e:
        print(str(e))

@app_commands.command(name='edit-task',description="Edits a given task")
@app_commands.describe(project_name='The name of the project to which the task belongs',task_num="The order of the task that you want edited")
async def bot_edit_task(interaction: discord.Interaction, project_name: str,task_num: int,new_task_name: str ):
    try:
        new_task_name=new_task_name.strip()
        await is_empty_new_task_name(interaction, new_task_name)

        await check_if_project_exist(interaction, project_name)

        tasks=Task.get_tasks_for_project_ordered(server_name=interaction.guild.name, project_name=project_name)
        await check_tasks_num(tasks=tasks, interaction=interaction, task_num=task_num)

        task_num-=1
        try:
            Task.update({Task.name : new_task_name}).where(
                (Task.name==tasks[task_num].name) & (Task.server_name == tasks[task_num].server_name)
            ).execute()
            tasks[task_num].name = new_task_name
        except IntegrityError as e:
            ...

        await interaction.response.send_message(
            embed=DiscordEmbdeddingFac.create_simple_dark_bg(
                title=f"Project[{project_name}] tasks:",
                body=list_task_for_project_name(server_name=interaction.guild.name,project_name=project_name,cached=tasks)
            )
        )
    except ValueError as e:
        print(str(e))


@app_commands.command(name='assign',description="Assigns a given project to a user")
@app_commands.describe(project_name='The name of the project you want to assign',task_num='The task number you want to assign to the user with the username provided')
async def bot_assign_task(interaction: discord.Interaction,project_name: str,task_num: int,member: discord.Member):
    try:
        await check_if_project_exist(interaction, project_name)

        tasks=Task.get_tasks_for_project_ordered(server_name=interaction.guild.name, project_name=project_name)
        await check_tasks_num(tasks=tasks, interaction=interaction, task_num=task_num)

        selected_task = tasks[task_num - 1]
        selected_task.assignee_username=member.name

        Task.update({Task.assignee_username : member.name}).where(
            (Task.project_name==project_name) & (Task.server_name == interaction.guild.name) & (Task.name==selected_task.name)
        ).execute()

        await interaction.response.send_message(
            embed=DiscordEmbdeddingFac.create_simple_dark_bg(
                title=f"Project[{project_name}] tasks:",
                body=list_task_for_project_name(server_name=interaction.guild.name,project_name=project_name,cached=tasks)
            )
        )

    except ValueError as e:
        print(str(e))

@app_commands.command(name='edit-assigment', description="Edits a given assigment" )
async def bot_edit_assigment(interaction:discord.Interaction, project_name: str,task_num: int,new_mem: discord.Member|None ):
    try:
        await check_if_project_exist(interaction, project_name)

        tasks = Task.get_tasks_for_project_ordered(server_name=interaction.guild.name, project_name=project_name)
        await check_tasks_num(tasks=tasks, interaction=interaction, task_num=task_num)

        selected_task = tasks[task_num - 1]
        new_assigment=new_mem.name if new_mem is not None else None

        selected_task.assignee_username=new_assigment
        Task.update({Task.assignee_username : new_assigment}).where(
            (Task.project_name == project_name) & (Task.server_name == interaction.guild.name) & \
            (Task.name == selected_task.name)
        ).execute()

        await interaction.response.send_message(
            embed=DiscordEmbdeddingFac.create_simple_dark_bg(
                title=f"Project[{project_name}] tasks:",
                body=list_task_for_project_name(server_name=interaction.guild.name, project_name=project_name,cached=tasks)
            )
        )
    except ValueError as e:
        print(str(e))