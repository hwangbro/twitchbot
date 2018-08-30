# General Commands for non-mod/non-admins go here

import api
import db
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
    return f'The command !{name} has been removed.'


def handle_meta_command(name, command_name='', command_text=''):
    if name == 'remove':
        return remove_command(command_name)
    elif name == 'add':
        return add_command(command_name, command_text)
    elif name == 'edit':
        return edit_command(command_name, command_text)
    else:
        return

commands_meta = {
    'commands': 'The commands for this channel are ' + ', '.join(['!' + x for x in sorted(commands_list.keys())])
}

if __name__ == '__main__':
    pass
