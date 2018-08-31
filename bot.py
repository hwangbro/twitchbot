# bot.py

import cfg
import socket
# from admin_commands import admin_commands, admin_commands_2
import api
import commands
import db
import points

from time import sleep, time
import importlib
import re
import requests
from multiprocessing import Process


def chat(sock, msg):
    """
    Sends a chat message through socket.
    :param sock: socket
    :param msg: string to be sent as message
    """
    sock.send("PRIVMSG {} :{}\r\n".format(cfg.CHAN, msg).encode("utf-8"))
    sleep(1 / cfg.RATE)


# def ban(sock, user):
#     chat(sock, ".ban {}".format(user))
#
#
# def timeout(sock, user, secs=600):
#     """
#     Time out a user for set period of time
#     """
#     chat(sock, ".timeout {}".format(user, secs))


def handle_command(sock, response) -> None:
    # importlib.reload(commands) refactor this
    username = re.search(r"\w+", response).group(0)
    message = cfg.CHAT_MSG.sub("", response)
    command_msg = re.match(r'^!([a-zA-Z0-9]*)$', message.strip().lower())
    #admin_command_msg = re.match(r'^!([a-zA-Z0-9]*) ([\w \!]*)$', message.strip())
    admin_command_msg = re.match(r'^!([a-zA-Z0-9]*) (.*)$', message.strip())
    meta_command_msg = re.match(r'^!([a-zA-Z0-9]*) !([\w]*)\s?(.*)$', message.strip())
    # print(username + ': ' + message)
    if command_msg is not None:
        command = command_msg.group(1)
        if command in commands.commands_list:
            chat(sock, commands.commands_list[command])
            return
        elif command in commands.commands_meta:
            chat(sock, commands.commands_meta[command])
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


def update_points():
    oldtime = time()
    while True:
        new = time()
        if new-oldtime > 60:
            oldtime = new
            points.update_viewers(api.get_viewers())


def main():
    s = socket.socket()
    s.connect((cfg.HOST,cfg.PORT))
    s.send("PASS {}\r\n".format(cfg.PASS).encode("utf-8"))
    s.send("NICK {}\r\n".format(cfg.NICK).encode("utf-8"))
    s.send("JOIN {}\r\n".format(cfg.CHAN).encode("utf-8"))

    p = Process(target=update_points)
    p.start()

    while True:
        response = s.recv(1024).decode("utf-8")
        if response == "PING :tmi.twitch.tv\r\n":
            s.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
        else:
            commands.handle_command(s, response)


def test():
    # url = 'https://api.twitch.tv/kraken/users?login=hwangbroxd'
    # headers = {'Client-ID': cfg.CLIENT_ID, 'Accept': 'application/vnd.twitchtv.v5+json',
    #            'Authorization': f'OAuth {cfg.TOKEN}'}
    # r = requests.get(url, headers=headers).json()
    # print(r['users'][0]['_id'])
    # url2 = 'https://api.twitch.tv/kraken/channels/'+cfg.CHANNEL_ID
    # r2 = requests.get(url2, headers=headers).json()
    # print(r2['display_name'], r2['status'], r2['game'])
    # print(r2)
    #
    # r3 = requests.get('https://api.twitch.tv/kraken/channels/{}/follows'.format(cfg.CHANNEL_ID), headers=headers).json()
    #
    # url6 = f'https://api.twitch.tv/kraken/channels/{cfg.CHANNEL_ID}/editors'
    # r6 = requests.get(url6, headers=headers)
    # print(r6)

    url7 = f'https://api.twitch.tv/kraken/streams/{cfg.CHANNEL_ID}'
    r7 = requests.get(url7, headers=cfg.HEADERS).json()
    # print(r7)
    print(r7)
    time = 0 if r7['stream'] is None else r7['stream']['created_at']
    print(type(time), time)

    r = requests.get(cfg.URL, headers=cfg.HEADERS).json()
    print(r['game'])
    print(api.get_game())
    print(commands_list['game'])


if __name__ ==  '__main__':
    main()
