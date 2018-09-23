# Main module for the bot. Run this to start.

import cfg
import socket
import api
import commands
import point_db

from time import sleep, time
import threading

def chat(sock, msg):
    '''Sends a chat message through socket.'''

    sock.send('PRIVMSG {} :{}\r\n'.format(cfg.CHAN, msg).encode('utf-8'))


def ban(sock, user):
    '''Bans the specified user from chat.'''

    chat(sock, '.ban {}'.format(user))


def timeout(sock, user, secs=600):
    '''Time out a user for set period of time.'''

    chat(sock, '.timeout {}'.format(user, secs))


def update_points():
    '''Update viewer points every minute.

    This function should be run in its own thread/process
    in order to maintain normal bot functionality.
    '''

    while True:
        sleep(60)
        point_db.update_viewers(api.get_viewers())


def main():
    s = socket.socket()
    s.connect((cfg.HOST,cfg.PORT))
    s.send('PASS {}\r\n'.format(cfg.PASS).encode('utf-8'))
    s.send('NICK {}\r\n'.format(cfg.NICK).encode('utf-8'))
    s.send('JOIN {}\r\n'.format(cfg.CHAN).encode('utf-8'))

    points_thread = threading.Thread(target=update_points)
    points_thread.daemon = True
    points_thread.start()

    while True:
        response = s.recv(1024).decode('utf-8')
        if response == 'PING :tmi.twitch.tv\r\n':
            s.send('PONG :tmi.twitch.tv\r\n'.encode('utf-8'))
        else:
            if 'PokPikachu' in response and 'monipooh' in response:
                chat(s, 'Pikachu LUL')
            else:
                print(response, end='')
                commands.handle_command(s, response)


if __name__ ==  '__main__':
    main()
