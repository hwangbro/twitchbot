# Module for interacting with the static commands database.

from peewee import *
from playhouse.shortcuts import *

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
	cmd = Commands.get_or_none(Commands.name==name)
	if cmd:
		return cmd.text

def get_command_list() ->{str:str}:
	return {c.name: c.text for c in Commands.select()}

def clear_commands():
    for cmd in Commands.select():
        cmd.delete_instance()

commands = {
    "brainpower": "O-oooooooooo AAAAE-A-A-I-A-U- JO-oooooooooooo AAE-O-A-A-U-U-A-E-eee-ee-eee AAAAE-A-E-I-E-A- JO-ooo-oo-oo-oo EEEEO-A-AAA-AAAA",
    "brna": "@photaiz is the best riven player I know.",
    "cubing": "https://pastebin.com/BVGyGZN3",
    "kms": "FeelsBadMan :gun:",
    "lydia": "A raging toxic flamer who only knows how to play toxic champions!! Report on sight!!",
    "opgg": "na.op.gg/summoner/userName=Hwangbro na.op.gg/summoner/userName=BoostedRivenMain na.op.gg/summoner/userName=darkfblazard na.op.gg/summoner/userName=Apathic",
    "riven": "By far the easiest champion in the game, and the most toxic as well. Only boosted monkeys play this champion, especially if they think they\"re good.",
    "xd": "bttvxD",
    "info": "This bot is a current work-in-progress. Type !commands for commands. If you have any suggestions or feedback, please let me know!",
    "moni": "support main monkaS",
    "ddlc": "4:10 UNLorD1: fucking monikammmmmmmmmmmmmmmmmmmmmmmmmmmmm",
    "tony": "OMEGALUL",
    "hack": "I'm in EZ",
    "pikachu": "LUL"
}
if __name__ == '__main__':
	test = get_command_list()
	print(test)