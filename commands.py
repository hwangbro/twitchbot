# General Commands for non-mod/non-admins go here

import api
import points
from pyparsing import Word, alphas, alphanums, restOfLine, Optional, Combine
from bot import chat
import cfg
import json

# To add, remove, or edit commands, the admin can type
# !add !command text here
# !edit !command text here
# !remove !command

commands_func_list = {
    'title': api.get_title,
    'game': api.get_game,
    'uptime': api.get_uptime,
    'botmasters': api.get_pro_mods,
}

meta_commands = ['remove', 'add', 'edit']

admin_commands = {
    'setgame': api.set_game,
    'settitle': api.set_title,
    'addpoints': points.add_points,
    'subpoints': points.sub_points,
    'setpoints': points.set_points,
}

parser = ":" + Word(alphanums+"_").setResultsName("username") + Word(alphanums+"_!@.") + "PRIVMSG" + "#hwangbroxd" + ":!" + Word(alphas).setResultsName("cmd") + Optional(Combine("!" + Word(alphanums))).setResultsName("new_cmd") + restOfLine.setResultsName("msg")

def load_commands():
    with open('commands.json', 'r') as f:
        return json.load(f)


commands_list = load_commands()


def save_commands(commands_list):
    with open('commands.json', 'w') as f:
        json.dump(commands_list, f, indent=4)


def add_command(name, command):
    global commands_list
    if name in commands_list:
        return f'!{name} already exists!'
    commands_list[name] = command
    save_commands(commands_list)
    commands_list = load_commands()
    return f'You\'ve successfully added the command !{name}'


def edit_command(name, command):
    global commands_list
    if name not in commands_list:
        return f'!{name} is not a command, cannot edit.'
    commands_list[name] = command
    save_commands(commands_list)
    commands_list = load_commands()
    return f'You\'ve successfully edited the command !{name}'


def remove_command(name):
    global commands_list
    if name not in commands_list:
        return f'!{name} is not an existing command.'
    del commands_list[name]
    save_commands(commands_list)
    commands_list = load_commands()
    return f'The command !{name} has been removed.'


def parse_command(response):
    print(response, end='')
    tmp = list(parser.scanString(response))
    if not tmp:
        return ('','','','')
    res = tmp[0][0]
    return res.username.strip().lower(), res.cmd.strip().lower(), res.new_cmd.strip().lower(), res.msg.strip()


def handle_command(sock, response) -> None:
    username, cmd, new_cmd, msg = parse_command(response)
    if cmd:
        if cmd in commands_list:
            chat(sock, commands_list[cmd])
        elif cmd in commands_func_list:
            chat(sock, commands_func_list[cmd]())
        elif cmd == 'commands':
            chat(sock, 'The commands for this channel are ' + ', '.join(['!' + x for x in sorted(list(commands_list.keys()) + list(commands_func_list.keys()))]))
        elif cmd == 'points':
            chat(sock, points.get_points(username.lower(), msg.lower()))
        elif cmd == 'gamble' and msg.isdigit():
            pass
        elif cmd in admin_commands and username in cfg.ADMIN:
            chat(sock, admin_commands[cmd](msg))
        elif cmd in meta_commands and new_cmd:
            chat(sock, handle_meta_command(cmd, new_cmd[1:], msg))
    return


def handle_meta_command(name, command_name='', command_text='') -> str:
    if name == 'remove':
        return remove_command(command_name)
    elif name == 'add':
        return add_command(command_name, command_text)
    elif name == 'edit':
        return edit_command(command_name, command_text)
    else:
        return

if __name__ == '__main__':
    pass
