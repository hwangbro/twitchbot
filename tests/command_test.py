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
