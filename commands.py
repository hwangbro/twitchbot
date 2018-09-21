# Command handling

import api
from bot import chat
import cfg
import point_db
import command_db

from pyparsing import Word, alphas, alphanums, restOfLine, Optional, Combine

# To add, remove, or edit commands, the admin can type
# !add !command text here
# !edit !command text here
# !remove !command

# Dictionary mapping commands to their respective function calls.
commands_func_list = {
    'title': api.get_title,
    'game': api.get_game,
    'uptime': api.get_uptime,
    'botmasters': api.get_pro_mods,
}

# Commands impacting other commands.
meta_commands = ['remove', 'add', 'edit']

# 'Admin' commands for point modifications.
point_commands = ['addpoints', 'subpoints', 'setpoints']

# 'Admin' commands for channel metadata modifications.
admin_commands = {
    'setgame': api.set_game,
    'settitle': api.set_title,
}

# Parser to grab command keywords from chat messages.
parser = ':' + Word(alphanums+'_').setResultsName('username') + Word(alphanums+'_!@.') + 'PRIVMSG' + '#hwangbroxd' + ':!' + Word(alphas).setResultsName('cmd') + Optional(Combine('!' + Word(alphanums))).setResultsName('new_cmd') + restOfLine.setResultsName('msg')


def parse_command(response) -> (str,):
    '''Parse the response for potential command formats'''

    parsed = list(parser.scanString(response))
    if not parsed:
        return ('','','','')
    res = parsed[0][0]
    return res.username.strip().lower(), res.cmd.strip().lower(), res.new_cmd.strip().lower(), res.msg.strip()


def handle_command(sock, response) -> None:
    '''Execute commands given by users.

    All command handling return strings to be
    printed out to the socket.
    '''

    # Parse the message for command keywords.
    username, cmd, new_cmd, msg = parse_command(response)
    username = username.lower()

    # If command is found
    if cmd:
        static = command_db.get_command(cmd)
        if static:
            chat(sock, static)
        elif cmd in commands_func_list:
            chat(sock, commands_func_list[cmd]())
        elif cmd == 'commands':
            commands_list = command_db.get_command_list()
            chat(sock, 'The commands for this channel are ' + ', '.join(['!' + x for x in sorted(list(commands_list.keys()) + list(commands_func_list.keys()))]))
        elif cmd == 'points':
            chat(sock, point_db.points_command(username, msg.lower()))
        elif cmd == 'gamble' and (msg.isdigit() or msg == 'all'):
            chat(sock, point_db.gamble(username, msg))
        elif cmd in point_commands and username in cfg.ADMIN:
            chat(sock, point_db.handle_point_command(cmd, msg))
        elif cmd in admin_commands and username in cfg.ADMIN:
            chat(sock, admin_commands[cmd](msg))
        elif cmd in meta_commands and new_cmd:
            chat(sock, handle_meta_command(cmd, new_cmd[1:], msg))
    return


def handle_meta_command(name, command_name='', command_text='') -> str:
    '''Properly handles meta commands.'''

    if name == 'remove':
        command_db.remove_command(command_name)
        return f"You've successfully removed the command {command_name}"
    elif name == 'add':
        command_db.add_command(command_name, command_text)
        return f"You've successfully added the command {command_name}"
    elif name == 'edit':
        command_db.edit_command(command_name, command_text)
        return f"You've successfully edited the command {command_name}"


if __name__ == '__main__':
    pass
