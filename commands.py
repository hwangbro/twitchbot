# Command handling

from time import sleep

from pyparsing import Word, alphas, alphanums, restOfLine, Optional, Combine

import api
import bot
import cfg
import point_db
import command_db
import chat_db


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

# List of commands for plebs
command_list = list(commands_func_list.keys())
command_list.extend(['points', 'gamble', 'challenge'])

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
username = Word(alphanums+'_').setResultsName('username')
irc_garb = Word(alphanums+'_!@.') + 'PRIVMSG' + '#hwangbroxd'
cmd = ':!' + Word(alphas).setResultsName('cmd')
new_cmd = Optional(Combine('!' + Word(alphanums))).setResultsName('new_cmd')
msg = restOfLine.setResultsName('msg')

parser = ':' + username + irc_garb + cmd + new_cmd + msg
chat_parser = ':' + username + irc_garb + ':' + msg


class Message:
    """Represents a chat message.

    Has methods to parse internally for different types of
    commands and to assign variables accordingly.
    """

    def __init__(self, text):
        self.username = self.message = self.command = self.metacommand = self.command_body = self.points_user = ''
        self.is_command = False

        self.is_points_command = False
        self.is_gamble_command = False
        self.is_challenge_command = False

        self.points_amount = 0

        self.parse_msg(text)
        self.parse_cmd(text)

        if (self.command in point_commands and self.username in cfg.ADMIN) or (self.command == 'challenge'):
            self.parse_points_command()

        elif self.command == 'gamble':
            self.parse_gamble_command()

    def parse_cmd(self, text):
        parsed = list(parser.scanString(text))
        if parsed:
            res = parsed[0][0]
            self.command = res.cmd.strip().lower()
            self.command_body = res.msg.strip()
            self.metacommand = res.new_cmd.strip().lower()
            self.is_command = self.metacommand != ''

    def parse_msg(self, text):
        parsed = list(chat_parser.scanString(text))
        if parsed:
            res = parsed[0][0]
            self.username = res.username.strip().lower()
            self.message = res.msg.strip()

    def parse_points_command(self):
        self.is_points_command = True
        message = self.command_body.split()
        try:
            self.points_user = message[0].replace('@', '')
            self.points_amount = int(message[1])
        except:
            print('incorrect points format for ' + str(message))
            return

    def parse_gamble_command(self):
        self.is_gamble_command = True
        try:
            if self.command_body:
                wager = self.command_body if self.command_body == 'all' else int(self.command_body)
            else:
                raise ValueError
        except:
            print('incorrect points format for ' + str(wager))
            return
        self.points_amount = wager

    def __str__(self):
        return f'[{self.username}]: {self.message}'


def handle_command(sock, response) -> None:
    """Execute commands given by users.

    All command handling return strings to be
    printed out to the socket.
    """

    msg = Message(response)
    if msg.username:
        chat_db.add_msg(msg.username, msg.message)
        print(msg)

    # If command is found
    if msg.command:
        static = command_db.get_command(msg.command)
        if static:
            bot.chat(sock, static)

        elif msg.username == 'monipooh' and 'pikachu' in msg.message:
            bot.chat(sock, 'Pikachu OMEGALUL')

        elif msg.command in commands_func_list:
            bot.chat(sock, commands_func_list[msg.command]())

        elif msg.command == 'commands':
            static_list = command_db.get_command_list()
            dynamic_list = ', '.join(['!' + x for x in sorted(list(static_list.keys()) + command_list)])
            bot.chat(sock, f'The commands for this channel are {dynamic_list}')

        elif msg.command == 'points':
            bot.chat(sock, point_db.points_command(msg))

        elif msg.command == 'gamble':
            bot.chat(sock, point_db.gamble(msg))

        elif msg.command == 'gamblestats':
            bot.chat(sock, point_db.gamblestats(msg))

        elif msg.command == 'challenge':
            bot.chat(sock, point_db.handle_challenge_command(msg))

        elif msg.command == 'cancel':
            bot.chat(sock, point_db.cancel_challenge(msg))

        elif msg.command == 'decline':
            bot.chat(sock, point_db.decline_challenge(msg))

        elif msg.command == 'accept':
            for line in point_db.accept_challenge(msg):
                bot.chat(sock, line)
                sleep(1.5)

        # addpoints, subpoints, setpoints
        elif msg.command in point_commands and msg.username in cfg.ADMIN:
            bot.chat(sock, point_db.handle_point_command(msg))

        # settitle, setgame
        elif msg.command in admin_commands and msg.username in cfg.ADMIN:
            bot.chat(sock, admin_commands[msg.command](msg.message))

        # add, edit, remove
        elif msg.command in meta_commands and msg.metacommand:
            bot.chat(sock, handle_meta_command(msg))#msg.command, msg.metacommand[1:], msg.message))

    return


def handle_meta_command(msg) -> str: #name, command_name='', command_text='') -> str:
    """Properly handles meta commands."""
    name = msg.command
    command_name = msg.metacommand[1:]
    command_text = msg.command_body
    if name == 'remove':
        command_db.remove_command(command_name)
        return f"You've successfully removed the command {command_name}"
    elif name == 'add':
        command_db.add_command(command_name, command_text)
        return f"You've successfully added the command {command_name}"
    elif name == 'edit':
        command_db.edit_command(command_name, command_text)
        return f"You've successfully edited the command {command_name}"


def space_command(msg):
    sep, *text = msg.split()
    text = ' '.join(text)
    return (' ' + sep + ' ').join(text)


if __name__ == '__main__':
    pass
