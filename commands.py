# General Commands for non-mod/non-admins go here

import api
import db
from pyparsing import Word, alphas, alphanums, restOfLine
from bot import chat
import cfg

# To add, remove, or edit commands, the admin can type
# !add !command text here
# !edit !command text here
# !remove !command

commands_list = {
    'title': f'Current Stream Title: {api.get_title()}',
    'game': f'hwangbroXD is currently playing {api.get_game()}',
    'uptime': api.get_uptime(),
    'botmasters': api.get_pro_mods(),
}

admin_commands = {
    'setgame': api.set_game,
    'settitle': api.set_title,
}

parser = "#" + Word(alphanums + "_").setResultsName("username") + ":!" + Word(alphas).setResultsName("cmd") + restOfLine.setResultsName("msg")

with open('commands.txt', 'r') as f:
    for line in f:
        key = eval(line.split(':')[0])
        val = eval(line.replace(key, '')[4:])[0]
        #val = eval(''.join(line.split(':')[1:]))[0]
        commands_list[key] = val


def add_command(name, command):
    if name in commands_list:
        return f'!{name} already exists!'
    with open('commands.txt', 'a') as f:
        f.write(f"'{name}': '{command}',\n")
        commands_list[name] = command
    return f'You\'ve successfully added the command !{name}'


def edit_command(name, command):
    if name not in commands_list:
        return f'!{name} is not a command, cannot edit.'
    with open('commands.txt', 'r+') as f:
        new_f = f.readlines()
        f.seek(0)
        for line in new_f:
            if f"'{name}'" in line:
                n_line = f"'{name}': '{command}',\n"
                f.write(n_line)
            else:
                f.write(line)
        f.truncate()
    commands_list[name] = command
    return f'You\'ve successfully edited the command !{name}'


def remove_command(name):
    if name not in commands_list:
        return f'!{name} is not an existing command.'
    with open('commands.txt', 'r+') as f:
        new_f = f.readlines()
        f.seek(0)
        for line in new_f:
            if f"'{name}'" not in line:
                f.write(line)
        f.truncate()
    del commands_list[name]
    return f'The command !{name} has been removed.'


def handle_command(sock, response) -> None:
    print(response, end='')
    tmp = list(parser.scanString(response))
    if not tmp:
        return
    username, cmd, msg = tmp[0][0].username.strip().lower(), tmp[0][0].cmd.strip().lower(), tmp[0][0].msg.strip().lower()
    if cmd:
        if cmd in commands_list:
            chat(sock, commands_list[cmd])
        elif cmd == 'commands':
            chat(sock, 'The commands for this channel are ' + ', '.join(['!' + x for x in sorted(commands_list.keys())]))
        elif cmd in admin_commands and username in cfg.ADMIN:
            chat(sock, admin_commands[cmd](msg))
            # chat(sock, admin_commands[])
    return
    
    #admin_command_msg = re.match(r'^!([a-zA-Z0-9]*) ([\w \!]*)$', message.strip())
    admin_command_msg = re.match(r'^!([a-zA-Z0-9]*) (.*)$', message.strip())
    meta_command_msg = re.match(r'^!([a-zA-Z0-9]*) !([\w]*)\s?(.*)$', message.strip())
    if command_msg is not None:
        command = command_msg.group(1)
        if command in commands.commands_list:
            chat(sock, commands.commands_list[command](msg))
            return
        elif command == 'points':
            chat(sock, db.get_points(username))
            return
    elif admin_command_msg is not None and admin_command_msg.group(1) in admin_commands and username.strip() in cfg.ADMIN:
        #print(admin_command_msg, admin_command_msg.group(1), admin_command_msg.group(2))
        chat(sock, admin_commands[admin_command_msg.group(1)](admin_command_msg.group(2)))
    elif meta_command_msg is not None and username.strip() in cfg.ADMIN:
        msg = commands.handle_meta_command(meta_command_msg.group(1), meta_command_msg.group(2), meta_command_msg.group(3))
        if msg is not None:
            chat(sock, msg)


def handle_meta_command(name, command_name='', command_text=''):
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
