# Module for chat history database.

from peewee import *

db = SqliteDatabase('db/chat_history.db', pragmas={
        'journal_mode': 'wal',
        'cache_size': -1 * 64000,
        'foreign_keys': 1,
        'ignore_check_constraints': 0,
        'synchronous': 0})

class BaseModel(Model):
	class Meta:
		database = db

class Chat(BaseModel):
	username = CharField()
	date = DateTimeField()
	message = CharField()