# Module to handle database read writes.

from peewee import *
import arrow
from random import randint

db = SqliteDatabase('twitchpoints.db')

class BaseModel(Model):
    class Meta:
        database = db

class Points(BaseModel):
    name = CharField(unique = True)
    points = IntegerField()
    modified = DateTimeField()

def update_viewers(usernames: [str]):
    empty_users = [{'name': user, 'points': 0, 'modified': arrow.now().format()} for user in usernames]
    Points.insert_many(empty_users).on_conflict(action='IGNORE').execute()
    query = Points.update(points = Points.points + 1).where(Points.name in usernames)
    query.execute()


def parse_points_command(msg) -> (str,int):
    message = msg.split()
    if len(message) != 2:
        return "Incorrect format."
    try:
        user, pts = message
        return user, int(pts)
    except:
        return "Incorrect format."


def handle_point_command(cmd, msg):
    name, pts = parse_points_command(msg)
    if cmd == 'addpoints':
        increment_points(name, pts, '+')
        return ""
    elif cmd == 'subpoints':
        increment_points(name, pts, '-')
        return ""
    elif cmd == 'setpoints':
        set_points(name, pts)
        return ""


def set_points(name, pts) -> str:
    query = Points.update(points = pts).where(Points.name == name).execute()


def increment_points(name, pts, type='+') -> str:
    empty = Points.insert([{'name': name, 'points': 0, 'modified': arrow.now().format()}]).on_conflict(action='IGNORE').execute()
    if type == '+':
        query = Points.update(points = Points.points + pts, modified = arrow.now().format()).where(Points.name == name)
    elif type == '-':
        query = Points.update(points = Points.points - pts, modified = arrow.now().format()).where(Points.name == name)
    query.execute()


def gamble(username, wager):
    user = Points.get(Points.name == username)
    points = user.points
    delta = (arrow.now() - arrow.get(user.modified)).seconds
    if (delta < 5):
        print("not enough time passed")
        return ""
    if wager < 0:
        print("can't bet negative numbers")
    roll = randint(1, 100)
    if wager > points:
        return "You don't have enough points to gamble."
    if roll > 50:
        increment_points(username, wager, "+")
        print("you won")
        # return f"You rolled a {str(roll)}! You've won {wager} points."
    else:
        increment_points(username, wager, "-")
        print("you lost")
        # return f"You rolled a {str(roll)}! You've lost {wager} points, loser."


def create_table():
    db.create_tables([Points])


def print_users():
    for user in Points.select():
        print(user.name, user.points)


def delete_all():
    for user in Points.select():
        user.delete_instance()


if __name__ == "__main__":
    db.connect()
    #create_table()
    print_users()
    # update_viewers(['hwangbroxd', 'asdf'])
    # create_table()
    # delete_all()
    # set_points('hwangbroxd', 25)
    gamble('hwangbroxd', 5)
    # handle_point_command("setpoints", "hwangbroxd 15")
    print_users()



























# db = sqlite3.connect('twitchpoints.db')
# c = db.cursor()

# #c.execute('CREATE TABLE viewer_points (ID INT PRIMARY KEY, USERNAME TEXT, POINTS INT);')
# #c.execute("INSERT INTO viewer_points (ID, USERNAME, POINTS) VALUES (1, 'hwangbroXD', 0)")
# cursor = c.execute("SELECT * FROM viewer_points")
# # for row in cursor:
# #     print(row)

# def update_viewer(username):
#     db = sqlite3.connect('twitchbot.db')
#     c = db.cursor()
#     c.execute('''SELECT POINTS from viewer_points WHERE USERNAME="{}"'''.format(username))
#     result = c.fetchone()
#     if result:
#         updated_points = result[0] + 1
#         c.execute('''UPDATE viewer_points set POINTS={} where USERNAME="{}"'''.format(updated_points, username))
#         c.execute('''SELECT POINTS from viewer_points WHERE USERNAME="{}"'''.format(username))
#         db.commit()
#     else:
#         c.execute('''INSERT INTO viewer_points (USERNAME, POINTS) VALUES ("{}", 0)'''.format(username.lower()))
#         db.commit()


# def get_points(username):
#     db = sqlite3.connect('twitchbot.db')
#     c = db.cursor()
#     c.execute('''SELECT POINTS from viewer_points WHERE USERNAME="{}"'''.format(username))
#     result = c.fetchone()
#     if result:
#         return '{}'.format(result[0])
#     else:
#         update_viewer(username)
#         return '0'

# def set_points(username, points):
#     db = sqlite3.connect('twitchbot.db')
#     c = db.cursor()
#     c.execute('''SELECT POINTS from viewer_points WHERE USERNAME="{}"'''.format(username))
#     result = c.fetchone()
#     if result:
#         updated_points = result[0] + points
#         c.execute('''UPDATE viewer_points set POINTS={} where USERNAME="{}"'''.format(updated_points, username))
#         c.execute('''SELECT POINTS from viewer_points WHERE USERNAME="{}"'''.format(username))
#         db.commit()
#     else:
#         c.execute('''INSERT INTO viewer_points (USERNAME, POINTS) VALUES ("{}", {})'''.format(username.lower(), points))
#         db.commit()
# # update_viewer('hwangbroxd')
# # print(get_points('hwangbroxd'))

