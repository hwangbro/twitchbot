# This module is in charge of making API calls

# TO-DO: refresh token checker
# fix auth

import cfg
import requests
import arrow

def get_new_token():
    #only run when token expires
    url = 'https://id.twitch.tv/oauth2/token?client_id={}&client_secret={}&grant_type=client_credentials&scope={}'.format(cfg.CLIENT_ID, cfg.secret, cfg.SCOPES)
    r = requests.post(url=url)
    print(r.json())


def get_uptime() -> str:
    url = f'https://api.twitch.tv/kraken/streams/{cfg.CHANNEL_ID}'
    #url = f'https://api.twitch.tv/helix/streams/{cfg.CHANNEL_ID}' to do
    r = requests.get(url, headers=cfg.HEADERS).json()
    if r['stream'] is None:
        return 'hwangbroXD is not live! '
    start_time = arrow.get(r['stream']['created_at'])
    duration = (arrow.now() - start_time).seconds
    min, sec = divmod(duration, 60)
    hr, min = divmod(min, 60)
    return 'hwangbroXD has been live for %d hours, %02d minutes and %02d seconds.' % (hr, min, sec)


def get_game() -> str:
    r = requests.get(cfg.URL, headers=cfg.HEADERS).json()
    return r['game']


def get_title() -> str:
    r = requests.get(cfg.URL, headers=cfg.HEADERS).json()
    return r['status']


def get_pro_mods() -> str:
    return f'The users who can use the admin bot commands are ' + ', '.join(cfg.ADMIN)


def set_game(game):
    if game.lower() == 'none':
        data = {'channel': {'game': ''}}
    else:
        data = {'channel': {'game': game}}
    requests.put(cfg.URL, headers=cfg.HEADERS, json=data)
    return f'The stream game has been updated to {game}'


def set_title(title):
    if len(title) > 140:
        return f'The stream title is too long and could not be set.'
    data = {'channel': {'status': title}}
    requests.put(cfg.URL, headers=cfg.HEADERS, json=data)
    return

def get_viewers() -> [str]:
    url = r'https://tmi.twitch.tv/group/user/hwangbroxd/chatters'
    r = requests.get(url).json()
    return r['chatters']['viewers']


def test():
    url = 'https://api.twitch.tv/kraken/users?login=hwangbroxd'
    headers = {'Client-ID': cfg.CLIENT_ID, 'Accept': 'application/vnd.twitchtv.v5+json',
               'Authorization': f'OAuth {cfg.TOKEN}'}
    r = requests.get(url, headers=headers).json()
    # print(r['users'][0]['_id'])
    url2 = 'https://api.twitch.tv/kraken/channels/'+cfg.CHANNEL_ID
    r2 = requests.get(url2, headers=headers).json()
    #print(r2['display_name'], r2['status'], r2['game'])
    #print(r2)

    r3 = requests.get('https://api.twitch.tv/kraken/channels/{}/follows'.format(cfg.CHANNEL_ID), headers=headers).json()

    url5 = 'https://api.twitch.tv/kraken/channels/'+cfg.CHANNEL_ID
    data = {"channel": {"status": "asdf", "game": "League of Legends"}}

    r5 = requests.put(url5, headers=headers, json=data)
    #print(r5)
    url6 = f'https://api.twitch.tv/kraken/channels/{cfg.CHANNEL_ID}/editors'
    r6 = requests.get(url6, headers=headers)
    #print(r6)

    url7 = f'https://api.twitch.tv/kraken/streams/{cfg.CHANNEL_ID}'
    r7 = requests.get(url7, headers=headers).json()
    #print(r7)
    get_viewers()

test()
