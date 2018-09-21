# Module to handle point database read writes.

from peewee import *
import arrow
from random import randint

db = SqliteDatabase('db/twitchpoints.db')


class BaseModel(Model):
    class Meta:
        database = db


class Points(BaseModel):
    name = CharField(unique = True)
    points = IntegerField()
    modified = DateTimeField()


def update_viewers(usernames: [str]):
    '''Adds one point to the specified users.

    Function takes in a list of users.
    If the users don't exist, add them into the database.
    After all the users are 'added', increment all the users by 1 point.
    '''

    empty_users = [{'name': user, 'points': 0, 'modified': arrow.now().format()} for user in usernames]
    Points.insert_many(empty_users).on_conflict(
        conflict_target=[Points.name],
        update={Points.points: Points.points + 1}).execute()


def get_points(username) -> str:
    '''Gets the point value of a single user.'''

    user = Points.get_or_none(Points.name == username)
    if user:
        return user.points
    return -1


def points_command(user1, user2):
    '''Handles the '!points' command.

    This handler is a bit more complex, given that
    you can check others points as well.
    user2 can be empty, which means you only check user1's points.
    '''

    user2exists = False
    if not user2:
        pts = get_points(user1)
    else:
        pts = get_points(user2)
        user2exists = True
    if pts == -1:
        return "You goofed. Try again nerd."
    user = user2 if user2exists else user1
    return f"{user} has {str(pts)} points!"


def parse_points_command(msg) -> (str,int):
    '''Parses the second portion of the meta points call.

    A sample example is:
        '!addpoints hwangbroxd 10'
    This function parses the 'hwangbroxd 10' and gets those two values.
    '''

    message = msg.split()
    if len(message) != 2:
        return "Incorrect format."
    try:
        user, pts = message
        return user, int(pts)
    except:
        return "Incorrect format."


def handle_point_command(cmd, msg):
    '''Overarching handler for meta point commands.'''

    name, pts = parse_points_command(msg)
    if cmd == 'addpoints':
        increment_points(name, pts, '+')
        return f"You have successfully added {str(pts)} points to {name}!"
    elif cmd == 'subpoints':
        increment_points(name, pts, '-')
        return f"You have successfully subtracted {str(pts)} points to {name}!"
    elif cmd == 'setpoints':
        set_points(name, pts)
        return f"{name} now has {str(pts)} points!"


def set_points(name, pts) -> str:
    '''Set point function.'''

    query = Points.update(points = pts).where(Points.name == name).execute()


def increment_points(name, pts, type='+') -> str:
    '''This function handles both adding and subtracting.'''

    empty = Points.insert([{'name': name, 'points': 0, 'modified': arrow.now().format()}]).on_conflict(action='IGNORE').execute()
    if type == '+':
        query = Points.update(points = Points.points + pts, modified = arrow.now().format()).where(Points.name == name)
    elif type == '-':
        query = Points.update(points = Points.points - pts, modified = arrow.now().format()).where(Points.name == name)
    query.execute()


def gamble(username, wager):
    '''Simple gambling function.

    Users can specify 'all' as the wager as well.
    Wager must be a positive number, less than the
    current amount of points a user has.
    '''

    user = Points.get(Points.name == username)
    points = user.points

    delta = (arrow.now() - arrow.get(user.modified)).seconds
    if (delta < 5):
        return "Be patient. Don't gamble too often."

    wager = points if wager == 'all' else int(wager)

    if wager < 0:
        return "Can't bet negative numbers."

    roll = randint(1, 100)
    if wager > points:
        return "You don't have enough points to gamble."
    if roll > 50:
        increment_points(username, wager, "+")
        return f"You rolled a {str(roll)}! You've won {wager} points. You now have {str(points + wager)} points."
    else:
        increment_points(username, wager, "-")
        return f"You rolled a {str(roll)}! You've lost {wager} points, loser. You now have {str(points - wager)} points."


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
    print_users()
    # update_viewers(['hwangbroxd', 'asdf'])
    # set_points('hwangbroxd', 25)
    # gamble('hwangbroxd', 5)
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

