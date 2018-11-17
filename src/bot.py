# Main module for the bot. Run this to start.

import itertools
import threading
import socket
from time import sleep, time
import signal
import sys

import cfg
import api
import commands
import point_db
import command_db
import chat_db
import counter_db


def chat(sock, msg):
    """Sends a chat message through socket."""

    sock.send(f'PRIVMSG {cfg.CHAN} :{msg}\r\n'.encode('utf-8'))


def ban(sock, user):
    """Bans the specified user from chat."""

    chat(sock, f'.ban {user}')


def timeout(sock, user, secs=600):
    """Time out a user for set period of time."""

    chat(sock, f'.timeout {user} {secs}')


def close_dbs():
    """Closes the connections to the dbs."""

    command_db.db.close()
    point_db.db.close()
    chat_db.db.close()
    counter_db.db.close()


class UpdatePoints(threading.Thread):
    """Update viewer points every minute."""

    def __init__(self):
        threading.Thread.__init__(self)
        self.event = threading.Event()

    def run(self):
        while not self.event.wait(15):
            point_db.update_viewers(api.get_viewers())
            point_db.clean_challenges()


class ChatThread(threading.Thread):

    def __init__(self, socket):
        threading.Thread.__init__(self)
        self.socket = socket
        self.event = threading.Event()
        self.messages = itertools.cycle([
            "Don't forget to SMASH that like button! Type !commands for a list of what this bot can do.",
            "Viewers gain points just by being in chat. Type !points to check how many points you have! Though, there's not much use to them yet...",
            "If you have any suggestions for the stream or this bot, please let me know in chat!"
            ])

    def run(self):
        while not self.event.wait(1200):
            chat(self.socket, next(self.messages))

def main():
    s = socket.socket()
    s.settimeout(0.5)
    s.connect((cfg.HOST, cfg.PORT))
    s.send(f'PASS {cfg.PASS}\r\n'.encode('utf-8'))
    s.send(f'NICK {cfg.NICK}\r\n'.encode('utf-8'))
    s.send(f'JOIN {cfg.CHAN}\r\n'.encode('utf-8'))
    chat(s, 'bot is alive')

    pts = UpdatePoints()
    pts.daemon = True
    pts.start()

    chitter = ChatThread(s)
    chitter.daemon = True
    chitter.start()

    def signal_handler(signal, frame):
        """Shuts down the UpdateThread and closes socket."""

        pts.event.set()
        chitter.event.set()
        close_dbs()
        chat(s, 'killing bot')
        s.shutdown(socket.SHUT_RDWR)
        s.close()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    while True:
        try:
            response = s.recv(1024).decode('utf-8')
            if response == 'PING :tmi.twitch.tv\r\n':
                s.send('PONG :tmi.twitch.tv\r\n'.encode('utf-8'))
            else:
                commands.handle_command(s, response)
        except socket.timeout:
            continue
        except Exception:
            chat(s, 'bot ded')
            raise


if __name__ == '__main__':
    main()
