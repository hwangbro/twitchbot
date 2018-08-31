import sqlite3

db = sqlite3.connect('twitchbot.db')
c = db.cursor()

#c.execute('CREATE TABLE viewer_points (ID INT PRIMARY KEY, USERNAME TEXT, POINTS INT);')
#c.execute("INSERT INTO viewer_points (ID, USERNAME, POINTS) VALUES (1, 'hwangbroXD', 0)")
cursor = c.execute("SELECT * FROM viewer_points")
# for row in cursor:
#     print(row)

def update_viewer(username):
    db = sqlite3.connect('twitchbot.db')
    c = db.cursor()
    c.execute('''SELECT POINTS from viewer_points WHERE USERNAME="{}"'''.format(username))
    result = c.fetchone()
    if result:
        updated_points = result[0] + 1
        c.execute('''UPDATE viewer_points set POINTS={} where USERNAME="{}"'''.format(updated_points, username))
        c.execute('''SELECT POINTS from viewer_points WHERE USERNAME="{}"'''.format(username))
        db.commit()
    else:
        c.execute('''INSERT INTO viewer_points (USERNAME, POINTS) VALUES ("{}", 0)'''.format(username.lower()))
        db.commit()


def get_points(username):
    db = sqlite3.connect('twitchbot.db')
    c = db.cursor()
    c.execute('''SELECT POINTS from viewer_points WHERE USERNAME="{}"'''.format(username))
    result = c.fetchone()
    if result:
        return '{}'.format(result[0])
    else:
        update_viewer(username)
        return '0'

def set_points(username, points):
    db = sqlite3.connect('twitchbot.db')
    c = db.cursor()
    c.execute('''SELECT POINTS from viewer_points WHERE USERNAME="{}"'''.format(username))
    result = c.fetchone()
    if result:
        updated_points = result[0] + points
        c.execute('''UPDATE viewer_points set POINTS={} where USERNAME="{}"'''.format(updated_points, username))
        c.execute('''SELECT POINTS from viewer_points WHERE USERNAME="{}"'''.format(username))
        db.commit()
    else:
        c.execute('''INSERT INTO viewer_points (USERNAME, POINTS) VALUES ("{}", {})'''.format(username.lower(), points))
        db.commit()
# update_viewer('hwangbroxd')
# print(get_points('hwangbroxd'))