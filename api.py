# This module is in charge of making API calls to Twitch

# TO-DO: refresh token checker
# work toward helix

import requests
from time import sleep

import arrow

import cfg

def get_new_token():
    # only run when token expires
    # OAuth Implicit Code Flow (on api site)
    # visit the url here for token
    auth = f'https://id.twitch.tv/oauth2/authorize?client_id={cfg.CLIENT_ID}&redirect_uri=https://twitchapps.com/tokengen/&response_type=token&scope={cfg.SCOPES}'


def get_uptime() -> str:
    '''Returns the uptime of the stream.'''

    url = f'https://api.twitch.tv/kraken/streams/{cfg.CHANNEL_ID}'
    r = requests.get(url, headers=cfg.HEADERS).json()

    # Sleep to avoid potential API timeouts.
    sleep(0.5)

    if r['stream'] is None:
        return 'hwangbroXD is not live!'

    start_time = arrow.get(r['stream']['created_at'])
    duration = (arrow.now() - start_time).seconds
    min, sec = divmod(duration, 60)
    hr, min = divmod(min, 60)
    return 'hwangbroXD has been live for %d hours, %02d minutes and %02d seconds.' % (hr, min, sec)


def get_game() -> str:
    '''Returns the current game category.'''

    r = requests.get(cfg.URL, headers=cfg.HEADERS).json()

    # Sleep to avoid potential API timeouts.
    sleep(0.5)

    return 'Current Game: ' + r['game']


def get_title() -> str:
    '''Returns the current stream title.'''

    r = requests.get(cfg.URL, headers=cfg.HEADERS).json()

    # Sleep to avoid potential API timeouts.
    sleep(0.5)

    return 'Current Stream Title: ' + r['status']


def get_pro_mods() -> str:
    '''Return a list of admins who can use meta bot commands.'''

    return f'The users who can use the admin bot commands are ' + ', '.join(cfg.ADMIN)


def set_game(game: str) -> str:
    '''Sets the game category of the stream.

    The game title has to exactly match a category.
    Otherwise, the category won't properly update.
    '''

    if game.lower() == 'none':
        data = {'channel': {'game': ''}}
    else:
        data = {'channel': {'game': game}}

    requests.put(cfg.URL, headers=cfg.HEADERS, json=data)

    # Sleep to avoid potential API timeouts.
    sleep(0.5)

    return f'The stream game has been updated to {game}'


def set_title(title: str) -> str:
    '''Sets the title of the stream.'''

    if len(title) > 140:
        return f'The stream title is too long and could not be set.'

    data = {'channel': {'status': title}}
    requests.put(cfg.URL, headers=cfg.HEADERS, json=data)

    # Sleep to avoid potential API timeouts.
    sleep(0.5)

    return f'The stream title has been set to ' + title


def get_viewers() -> [str]:
    '''Gets the number of viewers on the stream.'''

    url = r'https://tmi.twitch.tv/group/user/hwangbroxd/chatters'
    names = requests.get(url).json()

    # Sleep to avoid potential API timeouts.
    sleep(0.5)

    return names['chatters']['viewers'] + names['chatters']['moderators']
