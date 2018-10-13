# Module to handle point database read writes.

from peewee import *
import arrow
from random import randint

db = SqliteDatabase('db/twitchpoints.db', pragmas={
        'journal_mode': 'wal',
        'cache_size': -1 * 64000,
        'foreign_keys': 1,
        'ignore_check_constraints': 0,
        'synchronous': 0})


class BaseModel(Model):
    class Meta:
        database = db


class Points(BaseModel):
    name = CharField(unique = True)
    points = IntegerField(default = 0)
    modified = DateTimeField(default=arrow.now().format())
    points_won = IntegerField(default = 0)
    points_lost = IntegerField(default = 0)
    times_won = IntegerField(default = 0)
    times_lost = IntegerField(default = 0)
    challenges_won = IntegerField(default=0)
    challenges_lost = IntegerField(default=0)
    challenge_points_won = IntegerField(default=0)
    challenge_points_lost = IntegerField(default=0)


class Challenge(BaseModel):
    challenger = CharField()
    challenged = CharField()
    resolved = BooleanField(default=False)
    wager = IntegerField(default=0)
    winner = CharField(default="NONE")
    date = DateTimeField(default=arrow.now().format())


def create_challenge(user1, user2, wager):
    if user1 == user2:
        return("You can't challenge yourself.")
    query = Challenge.get_or_none(((Challenge.challenger == user1) | (Challenge.challenger == user2) | (Challenge.challenged == user1) | (Challenge.challenged == user2)) & (Challenge.resolved == False))
    if query:
        return("Challenge already found!!")
    else:
        if get_points(user1) < wager:
            return("You don't have enough points for this challenge.")
        if wager < 0:
            return("You can't wager a negative value.")
        query = Challenge.create(challenger=user1, challenged=user2, wager=wager)
        increment_points_without_update(user1, wager, '-')
        return(f"You have successfully created a challenge with {user2} for {wager} points. {user2}, type '!accept' or '!decline'")
        # print(query.challenger, query.challenged, query.resolved, query.wager, query.date)
        
    # 0) Check if unresolved challenge already exists with either user1 or user2
    # 1) check user1's points and see if they have enough
    # 2) subtract from user1's points (tentatively) **
    # 3) Create the challenge table entry


def check_challenge(user):
    query = Challenge.get_or_none(((Challenge.challenger == user) | (Challenge.challenged == user)) & (Challenge.resolved == False))
    if query:
        if query.challenger == user:
            print(f"You are challenging {query.challenged}")
        else:
            print(f"You are being challenged by {query.challenger}")
    else:
        print("You are currently not involved in a challenge.")


def clean_challenges():
    for chall in Challenge.select().where(Challenge.resolved==False):
        if (arrow.now() - arrow.get(chall.date)).seconds > 60:
            print(f"the challenge between {chall.challenger} and {chall.challenged} for {chall.wager} points has expired.")
            chall.resolved = True
            chall.winner = 'EXPIRED'
            chall.save()
            increment_points_without_update(chall.challenger, chall.wager, '+')

    # this runs every time update_viewers is called
    # go through all challenges that are unresolved
    # check if time has passed since date()
    # if enough time passed, reimburse the challenger with the wager
    # mark resolved, winner = NONE


def cancel_challenge(user):
    query = Challenge.get_or_none((Challenge.challenger == user) & (Challenge.resolved == False))
    if query:
        increment_points_without_update(query.challenger, query.wager, '+')
        query.resolved = True
        query.winner = 'CANCELLED'
        query.save()
        return (f"You have cancelled the challenge to {query.challenged}.")
    else:
        return "You're not currently in a challenge."

def decline_challenge(user):
    query = Challenge.get_or_none((Challenge.challenged == user) & (Challenge.resolved == False))
    if query:
        increment_points_without_update(query.challenger, query.wager, '+')
        query.resolved = True
        query.winner = 'DECLINED'
        query.save()
        return(f"The challenge from {query.challenger} has been declined.")
    else:
        return "You're not currently in a challenge."

def accept_challenge(user):
    query = Challenge.get_or_none((Challenge.challenged == user) & (Challenge.resolved == False))
    if query:
        if get_points(user) < query.wager:
            return(["You don't have enough points to accept the challenge"])
        else:
            increment_points_without_update(user, query.wager, '-')
            # return(f"accepting challenge from {query.challenger}")
            return(perform_challenge(query))
    else:
        return(["You dont have an active challenge."])
    # this runs when user accepts challenge
    # check if challenge expired, then check if user has enough points
    # if so, subtract (tentative) wager from challenged
    # call the function to execute the challenge


def perform_challenge(chall):
    # takes in the challenge object
    # roll twice, once for challenger, once for challenged
    # whoever rolls higher wins
    # add double the wager (for tentative) and add to points_won
    # mark as resolved, add name to winner field
    user1, user2 = get_user(chall.challenger), get_user(chall.challenged)
    ret = []
    ret.append(f"Initiating challenge between {chall.challenger} and {chall.challenged} for {chall.wager} points.")
    roll1, roll2 = randint(1,100), randint(1,100)
    ret.append(f"First roll: {chall.challenger} rolls a {roll1}")
    ret.append(f"Second roll: {chall.challenged} rolls a {roll2}")
    if roll1 == roll2:
        user1.challenge_points_lost += chall.wager
        user2.challenge_points_lost += chall.wager
        user1.save()
        user2.save()

        ret.append(f"You both rolled the same number! That means you both lose! Haha!")
        chall.winner = "TIE"
    else:
        if roll1 > roll2:
            ret.append(update_challenge_winner(user1, user2, chall.wager))
            chall.winner = chall.challenger
        elif roll2 > roll1:
            ret.append(update_challenge_winner(user2, user1, chall.wager))
            chall.winner = chall.challenged
    chall.resolved = True
    chall.save()
    return ret

def update_challenge_winner(winner, loser, wager):
    winner.challenge_points_won += wager
    loser.challenge_points_lost += wager
    winner.challenges_won += 1
    loser.challenges_lost += 1
    winner.points += wager * 2
    winner.save()
    loser.save()
    return f"{winner.name} wins {wager} points! Better luck next time, {loser.name}."


def handle_challenge_command(user, msg):
    try:
        user2, wager = parse_points_command(msg)
        return(create_challenge(user, user2, wager))
    except ValueError:
        return "Incorrect Format."
    


def update_viewers(usernames: [str]):
    '''Adds one point to the specified users.

    Function takes in a list of users.
    If the users don't exist, add them into the database.
    After all the users are 'added', increment all the users by 1 point.
    '''

    empty_users = [{'name': user} for user in usernames]
    Points.insert_many(empty_users).on_conflict(
        conflict_target=[Points.name],
        update={Points.points: Points.points + 1}).execute()


def get_points(username) -> int:
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
    user1 = user1.replace("@", '')
    user2 = user2.replace("@", '')
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
    try:
        user, pts = message
        return user.replace("@", ""), int(pts)
    except ValueError:
        return "Incorrect format."


def handle_point_command(cmd, msg):
    '''Overarching handler for meta point commands.'''

    name, pts = parse_points_command(msg)
    empty = Points.insert([{'name': name}]).on_conflict(action='IGNORE').execute()
    if cmd == 'addpoints':
        increment_points_without_update(name, pts, '+')
        return f"You have successfully added {str(pts)} points to {name}!"
    elif cmd == 'subpoints':
        increment_points_without_update(name, pts, '-')
        return f"You have successfully subtracted {str(pts)} points to {name}!"
    elif cmd == 'setpoints':
        set_points(name, pts)
        return f"{name} now has {str(pts)} points!"


def set_points(name, pts) -> str:
    '''Set point function.'''

    query = Points.update(points = pts).where(Points.name == name).execute()


def increment_points(name, pts, type='+') -> str:
    '''This function handles both adding and subtracting.'''

    empty = Points.insert([{'name': name}]).on_conflict(action='IGNORE').execute()
    if type == '+':
        query = Points.update(points = Points.points + pts, points_won = Points.points_won + pts, times_won = Points.times_won + 1, modified = arrow.now().format()).where(Points.name == name)
    elif type == '-':
        query = Points.update(points = Points.points - pts, points_lost = Points.points_lost + pts, times_lost = Points.times_lost + 1, modified = arrow.now().format()).where(Points.name == name)
    query.execute()


def increment_points_without_update(name, pts, type='+') -> str:
    '''This function handles both adding and subtracting.'''

    empty = Points.insert([{'name': name}]).on_conflict(action='IGNORE').execute()
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

    user = get_user(username)
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


def delta_points(user) -> str:
    user = get_user(user)
    total = user.points_won - user.points_lost
    res = "profit" if total > 0 else "deficit"
    return f"You have a lifetime {res} of {total} points."


def get_point_win_total(user) -> str:
    user = get_user(user)
    won = user.points_won
    return f"You have won {won} points total."


def get_point_lost_total(user) -> str:
    user = get_user(user)
    lost = user.points_lost
    return f"You have lost {lost} points total."


def get_gamble_win_total(user) -> str:
    user = get_user(user)
    won = user.times_won
    return f"You have won {won} gambling endeavors total."


def get_gamble_loss_total(user) -> str:
    user = get_user(user)
    lost = user.times_lost
    return f"You have lost {lost} gambling endeavors total."


def get_user(username) -> Points:
    user = Points.get_or_create(name = username)
    return user[0]


def create_table():
    db.create_tables([Points, Challenge])


def print_users():
    for user in Points.select():
        print(user.name, user.points)
        print("\tchallenges won: ", user.challenges_won)
        print("\tchallenges lost:", user.challenges_lost)


def print_challenges():
    for challenge in Challenge.select():
        print(challenge.challenger, challenge.challenged, challenge.wager, challenge.resolved)


if __name__ == "__main__":
    db.connect()
    # create_table()
    print_users()
    # create_challenge('hwangbroxd', 'unlord1', 9)
    # accept_challenge('unlord1')
    # update_viewers(['hwangbroxd', 'gay_zach'])
    # set_points('hwangbroxd', 25)
    # gamble('hwangbroxd', 5)
    # handle_point_command("setpoints", "hwangbroxd 15")
    # print_users()



























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

