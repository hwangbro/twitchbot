import sys, os
sys.path.insert(0, os.path.abspath('../src'))

import commands
import cfg


class TestMessage(object):
	def test_basic_init(self):
		chat_msg = ":hwangbroxd!hwangbroxd@hwangbroxd.tmi.twitch.tv PRIVMSG #hwangbroxd :test"
		msg = commands.Message(chat_msg)
		assert msg.username == 'hwangbroxd'
		assert msg.message == 'test'
		assert msg.command == ''
		assert msg.metacommand == ''
		assert msg.command_body == ''
		assert msg.points_user == ''
		assert msg.is_command == False
		assert msg.is_admin == True
		assert msg.points_amount == 0

	def test_command_init(self):
		chat_msg = ":hwangbroxd!hwangbroxd@hwangbroxd.tmi.twitch.tv PRIVMSG #hwangbroxd :!commands"
		msg = commands.Message(chat_msg)
		assert msg.command == 'commands'

	def test_admin_command_init(self):
		chat_msg = ":hwangbroxd!hwangbroxd@hwangbroxd.tmi.twitch.tv PRIVMSG #hwangbroxd :!add !test Kappa"
		msg = commands.Message(chat_msg)
		assert msg.command == 'add'
		assert msg.is_admin == True
		assert msg.metacommand == 'test'
		assert msg.command_body == 'Kappa'

	def test_point_init(self):
		chat_msg = ":hwangbroxd!hwangbroxd@hwangbroxd.tmi.twitch.tv PRIVMSG #hwangbroxd :!points"
		msg = commands.Message(chat_msg)
		assert msg.command == 'points'
		assert msg.points_amount == 0

	def test_meta_point_init(self):
		chat_msg = ":hwangbroxd!hwangbroxd@hwangbroxd.tmi.twitch.tv PRIVMSG #hwangbroxd :!addpoints gay_zach 2"
		msg = commands.Message(chat_msg)
		assert msg.command == 'addpoints'
		assert msg.points_user == 'gay_zach'
		assert msg.points_amount == 2
		assert msg.is_admin

	def test_gamble_init(self):
		chat_msg = ":hwangbroxd!hwangbroxd@hwangbroxd.tmi.twitch.tv PRIVMSG #hwangbroxd :!gamble 20"
		msg = commands.Message(chat_msg)
		assert msg.points_amount == 20

	def test_challenge_init(self):
		chat_msg = ":hwangbroxd!hwangbroxd@hwangbroxd.tmi.twitch.tv PRIVMSG #hwangbroxd :!challenge gay_zach 20"
		msg = commands.Message(chat_msg)
		assert msg.points_amount == 20
		assert msg.points_user == 'gay_zach'

class TestHandleCommand(object):
	def test_no_command(self):
		chat_msg = ":hwangbroxd!hwangbroxd@hwangbroxd.tmi.twitch.tv PRIVMSG #hwangbroxd :Hello World"
		

class TestHandleMetaCommand(object):
	def test_add(self):
		chat_msg = ":hwangbroxd!hwangbroxd@hwangbroxd.tmi.twitch.tv PRIVMSG #hwangbroxd :!add !test Kappa"
		msg = commands.Message(chat_msg)
		output = commands.handle_meta_command(msg)
		assert output == "You've successfully added the command test"

	def test_edit(self):
		chat_msg = ":hwangbroxd!hwangbroxd@hwangbroxd.tmi.twitch.tv PRIVMSG #hwangbroxd :!edit !test KappaPride"
		msg = commands.Message(chat_msg)
		output = commands.handle_meta_command(msg)
		assert output == "You've successfully edited the command test"

	def test_remove(self):
		chat_msg = ":hwangbroxd!hwangbroxd@hwangbroxd.tmi.twitch.tv PRIVMSG #hwangbroxd :!remove !test"
		msg = commands.Message(chat_msg)
		output =  commands.handle_meta_command(msg)
		assert output == "You've successfully removed the command test"


class TestSpaceCommand(object):
	def test_one(self):
		test_input = 'haHAA ABC'
		output = commands.space_command(test_input)
		assert output == 'A haHAA B haHAA C'

	def test_two(self):
		test_input = 'LUL Hi Mom'
		output = commands.space_command(test_input)
		assert output == 'H LUL i LUL   LUL M LUL o LUL m'
