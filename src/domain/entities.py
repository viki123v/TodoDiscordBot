from peewee import Model, CharField, CompositeKey, ForeignKeyField
from . import db_con

class Project(Model):
    server_name = CharField(unique=True,null=False,max_length=200,column_name='server_name')
    name = CharField(null=False,max_length=200,column_name='name')

    class Meta:
        database = db_con
        primary_key = CompositeKey('server_name', 'name')
        table_name='projects'

class Task(Model):
    name = CharField(null=False,column_name='name',max_length=200)
    server_name=ForeignKeyField(Project,to_field='server_name',lazy_load=False,null=False,column_name='server_name')
    project_name=ForeignKeyField(Project,to_field='name',lazy_load=False,null=False,column_name='project_name')
    assignee_username=CharField(null=True,max_length=100,column_name='assignee')

    @staticmethod
    def get_tasks_for_project_ordered(project_name : str, server_name: str):
        return Task.select().where((Task.project_name == project_name) & (Task.server_name == server_name)).order_by(Task.name)

    class Meta:
        database = db_con
        primary_key = CompositeKey('name','server_name','project_name')
        table_name='tasks'
