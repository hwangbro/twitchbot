# types of commands
# 1) commands with no arguments, static output
# 		!xd, !brna
# 2) commands with 1+ argument, dynamic output
#		!ban ____
# 3) commands where user is argument
# 		!points
# 4) admin commands (with or without arguments)
asdf = "asjdfkl;a"
test_str = r":hwangbroxd!hwangbroxd@hwangbroxd.tmi.twitch.tv PRIVMSG #hwangbroxd :!lfjdk"

from pyparsing import Word, alphas, alphanums, restOfLine, Suppress, Optional, Combine
parser = ":" + Word(alphanums+"_").setResultsName("username") + Word(alphanums+"_!@.") + "PRIVMSG" + "#hwangbroxd" + ":!" + Word(alphas).setResultsName("cmd") + Optional(Word("!"+alphanums)).setResultsName("new_cmd") + restOfLine.setResultsName("msg")

test = "help 4"
name, points = test.split()

def parsetest():
	command = "!" + Word(alphas).setResultsName("command") + restOfLine.setResultsName("arg")
	message = "#" + Word(alphanums + "_").setResultsName("username") + ":!" + Word(alphas).setResultsName("cmd") + restOfLine.setResultsName("msg")
	# for t,s,e in command.scanString(test_str):
	# 	print("command:",t.command, "\nextra:", str.lstrip(t.arg))
	x = list(message.scanString(test_str))
	if x:
		print(x[0][0].username, x[0][0].cmd, 'msg:', x[0][0].msg)
	ff = message.scanString(test_str)
	if list(ff):
		print("alive")
	# for t,s,e in message.scanString(test_str):
	# 	print(t.username, ":", t.msg)

#parsetest()

import api
import cfg
import requests, cfg
#url = '''https://id.twitch.tv/oauth2/token?client_id={}&client_secret={}&grant_type=client_credentials&scope=user:edit:broadcast user:edit'''.format(cfg.CLIENT_ID, cfg.secret)
#url = r'https://id.twitch.tv/oath2/token?client_id={}&client_secret={}&grant_type=client_credentials&scope=user:read:broadcast'.format(cfg.CLIENT_ID, cfg.secret)
#r = requests.get(r'http://id.twitch.tv/oath2/validate', headers={'Authorization': 'OAuth ' + cfg.TOKEN})
data = {'channel': {'game': 'League of Legends'}}
r = requests.put(cfg.URL, headers=cfg.HEADERS, json=data)
#print(r.json())

# print(api.get_viewers())

def set_game(game):
    if game.lower() == 'none':
        data = {'channel': {'game': ''}}
    else:
        data = {'channel': {'game': game}}
    r = requests.put(cfg.URL, headers=cfg.HEADERS, json=data)
    print(r.json())
    return f'The stream game has been updated to {game}'

#set_game("League of Legends")
URL = 'https://api.twitch.tv/kraken/channels/31561772/editors'
r2 = requests.get(url=URL, headers=cfg.HEADERS)
#print(r2.json())

# r = requests.get(url=auth, headers={'Accept': 'application/vnd.twitchtv.v5+json'})
import random
# print(random.randint(1, 100))
# print(test['b'])
from os import getcwd


from playsound import playsound
playsound(r'D:\Miscellaneous\Independent_Projects\twitchbot\sounds\oof.mp3')