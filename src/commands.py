import discord
from typing import cast
from discord import app_commands

@app_commands.command(name='show-todo')
async def show(interaction: discord.Interaction):
    response=cast(discord.InteractionResponse,interaction.response)

    embded=discord.Embed(
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

@app_commands.command(name='add-project',
                      description="Creates a new project, if there isn't one with the same name")
@app_commands.describe(project_name='The name of the project you want to add')
async def bot_add_project(interaction: discord.Interaction,
                              project_name: str):
    pass

@app_commands.command(name='remove-project',
                      description="Removes a given project")
@app_commands.describe(project_name='The name of the project you want to remove')
async def bot_remove_project(interaction: discord.Interaction,
                         project_name: str):
    pass

@app_commands.command(name='assign',
                      description="Assigns a given project to a user")
@app_commands.describe(project_name='The name of the project you want to assign',
                       task_num='The task number you want to assign to the user with the username provided ',
                       username="The username of the user, you want to assign to this task")
async def bot_assign_project_to_member(interaction: discord.Interaction,
                                project_name:str,
                                task_num: int,
                                username:str):
    pass

@app_commands.command(name='take-on',
                      description="Assign to your self a task from a given project")
@app_commands.describe(project_name='The name of the project you want take',
                       task_num='The task number you want to take up on ',)
async def bot_take_on_project(interaction: discord.Interaction,
                                project_name:str,
                                task_num: int):
    pass

@app_commands.command(name='drop-assigment',
                      description="Unassigns a given task")
@app_commands.describe(project_name='The name of the project, in which the task belongs',
                       task_num='The task number you want to drop assigment')
async def bot_drop_assigment(interaction: discord.Interaction,
                         project_name: str,
                         task_num: int):
    pass


@app_commands.command(name="list-tasks",
                      description="Shows the tasks registered to a given project")
@app_commands.describe(project_or_username='The name of the project or user which tasks you want list')
async def bot_list_tasks(interaction: discord.Interaction,
                     project_or_username:str):
    pass

@app_commands.command(name='complete-task',
                      description="Marks a task as completed and removes it")
@app_commands.describe(project_name="The name of the project to which the task belongs",
                       task_num="The order of the task that you completed")
async def bot_mark_task_as_completed(interaction: discord.Interaction,
                                 project_name: str,
                                 task_num: int):
    pass

@app_commands.command(name='edit-task',
                      description="Edits a given task")
@app_commands.describe(project_name='The name of the project to which the task belongs',
                       task_num="The order of the task that you want edited")
async def bot_edit_task(interaction:discord.Interaction,
                    project_name: str,
                    task_num: int,):
    pass


@app_commands.command(name='add-task',
                      description="Create a new task")
@app_commands.describe(project_name="The name of the project to which you want to add a task",
                       task_name='The name of the new task')
async def bot_add_task(interaction:discord.Interaction, project_name: str, task_name:str):
    pass



