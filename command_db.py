# Module for interacting with the static commands database.

from peewee import *

db = SqliteDatabase('static_commands.db')

class BaseModel(Model):
    class Meta:
        database = db

class Commands(BaseModel):
    name = CharField(unique = True)
    text = CharField()


def add_command(name, text):
	Commands.insert(name=name, text=text).execute()

def remove_command(name):
	Commands.delete().where(Commands.name == name).execute()

def edit_command(name, text):
	Commands.replace(name=name, text=text).execute()

def get_command(name):
	cmd = Commands.get_or_none(name==name)
	if cmd:
		return cmd.text
