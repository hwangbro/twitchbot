import sys, os
sys.path.insert(0, os.path.abspath('../src'))

import commands

class TestMessage(object):
	def test_one(self):
		assert 1 == 1

class TestHandleCommand(object):
	def test_one(self):
		assert 2 == 2

class TestHandleMetaCommand(object):
	def test_one(self):
		assert 3 == 3

class TestSpaceCommand(object):
	def test_one(self):
		test_input = 'haHAA ABC'
		output = commands.space_command(test_input)
		assert output == 'A haHAA B haHAA C'

	def test_two(self):
		test_input = 'LUL Hi Mom'
		output = commands.space_command(test_input)
		assert output == 'H LUL i LUL   LUL M LUL o LUL m'
