# Module for chat history database.

from peewee import *
import arrow

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

def add_msg(user, msg):
	if user and msg:
		Chat.insert(username=user, message=msg, date=arrow.now().format())

if __name__ == '__main__':
	# tables = db.get_tables()
	# print(tables)
	pass