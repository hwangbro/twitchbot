# Module to handle point database read writes.

from random import randint

from peewee import *
import arrow


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
    name = CharField(unique=True)
    points = IntegerField(default=150)
    modified = DateTimeField(default=arrow.now().format())
    points_won = IntegerField(default=0)
    points_lost = IntegerField(default=0)
    times_won = IntegerField(default=0)
    times_lost = IntegerField(default=0)
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
    """Creates a challenge between two users
     Points are initially subtracted from user1 until the challenge
    is either accepted or declined. If declined or cancelled,
    user1 gets points back.
    """

    if user1 == user2:
        return("You can't challenge yourself.")
    query = Challenge.get_or_none(((Challenge.challenger == user1)
                                  | (Challenge.challenger == user2)
                                  | (Challenge.challenged == user1)
                                  | (Challenge.challenged == user2))
                                  & (Challenge.resolved == False))
    if query:
        return("Challenge already found!!")
    else:
        if get_points(user1) < wager:
            return(f'{user1} only has {pts} points, not enough for this challenge.')
        if wager < 0:
            return("You can't wager a negative value.")
        query = Challenge.create(challenger=user1, challenged=user2, wager=wager, date=arrow.now().format())
        increment_points_without_update(user1, wager, '-')
        return(f"{user1} has successfully created a challenge with {user2} for {wager} points. {user2}, please type '!accept' or '!decline'")


def clean_challenges():
    """Expires challenges if they are active for over a minute."""

    for chall in Challenge.select().where(Challenge.resolved == False):
        if (arrow.now() - arrow.get(chall.date)).seconds > 120:
            print(f"the challenge between {chall.challenger} and {chall.challenged} for {chall.wager} points has expired.")
            chall.resolved = True
            chall.winner = 'EXPIRED'
            chall.save()
            increment_points_without_update(chall.challenger, chall.wager, '+')


def cancel_challenge(msg):
    """Cancels a challenge that the user sent out."""

    user = msg.username
    query = Challenge.get_or_none((Challenge.challenger == user) & (Challenge.resolved == False))
    if query:
        increment_points_without_update(query.challenger, query.wager, '+')
        query.resolved = True
        query.winner = 'CANCELLED'
        query.save()
        return f"{user} has cancelled the challenge to {query.challenged}."
    else:
        return "f{user} is not currently in a challenge."


def decline_challenge(msg):
    """Allows a challenged to decline a challenge."""

    user = msg.username
    query = Challenge.get_or_none((Challenge.challenged == user) & (Challenge.resolved == False))
    if query:
        increment_points_without_update(query.challenger, query.wager, '+')
        query.resolved = True
        query.winner = 'DECLINED'
        query.save()
        return f'{user} is a coward and declined the challenge from {query.challenger}.'
    else:
        return f'{user} is not currently in a challenge.'


def accept_challenge(msg):
    """Handles the accept challenge sequence."""

    user = msg.username
    query = Challenge.get_or_none((Challenge.challenged == user) & (Challenge.resolved == False))
    if query:
        if get_points(user) < query.wager:
            return([f"{user} doesn't have enough points to accept the challenge"])
        else:
            increment_points_without_update(user, query.wager, '-')
            return(perform_challenge(query))
    else:
        return([f"{user} doesn't have an active challenge."])


def perform_challenge(chall):
    """Executes the challenge between two users.
    This function takes in the challenge DB object.
    Due to constraints in the chat method, the return type is a list
    of strings to send to chat one by one.
    """

    user1, user2 = get_user(chall.challenger), get_user(chall.challenged)
    ret = []
    ret.append(f'Initiating challenge between {chall.challenger} and {chall.challenged} for {chall.wager} points.')
    roll1, roll2 = randint(1, 100), randint(1, 100)
    ret.append(f'First roll: {chall.challenger} rolls a {roll1}')
    ret.append(f'Second roll: {chall.challenged} rolls a {roll2}')
    if roll1 == roll2:
        user1.challenge_points_lost += chall.wager
        user2.challenge_points_lost += chall.wager
        user1.save()
        user2.save()

        ret.append(f'You both rolled the same number! That means you both lose! Haha!')
        chall.winner = 'TIE'
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
    """Updates db entries with challenge results"""

    winner.challenge_points_won += wager
    loser.challenge_points_lost += wager
    winner.challenges_won += 1
    loser.challenges_lost += 1
    winner.points += wager * 2
    winner.save()
    loser.save()
    return f'{winner.name} wins {wager} points! Better luck next time, {loser.name}.'


def handle_challenge_command(msg):
    """Parses the message for proper challenge format.

    This function also redirects cancel and decline commands
    to the respective functions.
    """
    user = msg.username
    cmd = msg.message
    wager = msg.points_amount
    user2 = msg.points_user

    if cmd == 'decline':
        return decline_challenge(user)
    elif cmd == 'cancel':
        return cancel_challenge(user)
    elif wager <= 0:
        return "No challenge created."
    return(create_challenge(user, user2, wager))


def update_viewers(usernames: [str]):
    """Adds one point to the specified users.

    Function takes in a list of users.
    If the users don't exist, add them into the database.
    After all the users are 'added', increment all the users by 1 point.
    """

    empty_users = [{'name': user} for user in usernames]
    Points.insert_many(empty_users).on_conflict(
        conflict_target=[Points.name],
        update={Points.points: Points.points + 1}).execute()
    Points.update(points=Points.points + 49).where(Points.name == 'hwangbroxd')


def get_points(username) -> int:
    """Gets the point value of a single user."""

    user = Points.get_or_none(Points.name == username)
    if user:
        return user.points
    return 0


def points_command(msg):
    """Handles the '!points' command.

    This handler is a bit more complex, given that
    you can check others points as well.
    user2 can be empty, which means you only check user1's points.
    """

    user1 = msg.username
    user2 = msg.command_body

    user2exists = False
    user1 = user1.replace('@', '')
    user2 = user2.replace('@', '')
    if not user2:
        pts = get_points(user1)
    else:
        pts = get_points(user2)
        user2exists = True
    user = user2 if user2exists else user1
    return f'{user} has {pts} points!'


def parse_points_command(msg) -> (str, int):
    """Parses the second portion of the meta points call.

    A sample example is:
        '!addpoints hwangbroxd 10'
    This function parses the 'hwangbroxd 10' and gets those two values.
    """

    message = msg.split()
    try:
        user, pts = message
        return user.replace('@', ''), int(pts)
    except ValueError:
        return 'Incorrect format.'


def handle_point_command(msg):
    """Overarching handler for meta point commands."""

    name = msg.points_user
    pts = msg.points_amount
    cmd = msg.command
    Points.insert([{'name': name}]).on_conflict(action='IGNORE').execute()
    if cmd == 'addpoints':
        increment_points_without_update(name, pts, '+')
        return f'You have successfully added {pts} points to {name}!'
    elif cmd == 'subpoints':
        increment_points_without_update(name, pts, '-')
        return f'You have successfully subtracted {pts} points to {name}!'
    elif cmd == 'setpoints':
        set_points(name, pts)
        return f'{name} now has {pts} points!'


def set_points(name, pts) -> str:
    """Set point function."""

    query = Points.update(points=pts).where(Points.name == name).execute()


def increment_points(name, pts, type='+') -> str:
    """This function handles both adding and subtracting."""

    empty = Points.insert([{'name': name}]).on_conflict(action='IGNORE').execute()
    if type == '+':
        query = Points.update(points=Points.points + pts,
                              points_won=Points.points_won + pts,
                              times_won=Points.times_won + 1,
                              modified=arrow.now().format()).where(Points.name == name)
    elif type == '-':
        query = Points.update(points=Points.points - pts,
                              points_lost=Points.points_lost + pts,
                              times_lost=Points.times_lost + 1,
                              modified=arrow.now().format()).where(Points.name == name)
    query.execute()


def increment_points_without_update(name, pts, type='+') -> str:
    """This function handles both adding and subtracting."""

    empty = Points.insert([{'name': name}]).on_conflict(action='IGNORE').execute()
    if type == '+':
        query = Points.update(points=Points.points + pts, modified=arrow.now().format()).where(Points.name == name)
    elif type == '-':
        query = Points.update(points=Points.points - pts, modified=arrow.now().format()).where(Points.name == name)
    query.execute()


def gamble(msg):
    """Simple gambling function.

    Users can specify 'all' as the wager as well.
    Wager must be a positive number, less than the
    current amount of points a user has.
    """
    username = msg.username
    wager = msg.points_amount

    user = get_user(username)
    points = user.points

    delta = (arrow.now() - arrow.get(user.modified)).seconds
    if (delta < 5):
        return "Be patient. Don't gamble too often."

    if wager == 'all':
        wager = points

    if wager < 0:
        return "Can't bet negative numbers."

    roll = randint(45, 100) if username == 'hwangbroxd' else randint(0, 100)
    if wager > points:
        return f"{username} only has {points} points. You don't have enough to gamble."
    if roll == 0:
        increment_points(username, points, "-")
        return f"{username}, the poor unlucky soul, rolled a {roll}. You've lost all your points. You now have 0 points."
    if roll == 100:
        increment_points(username, points, "+")
        return f"Are you cheating?? {username} rolled a {roll}. You've doubled your points, and now have {points*2} points!"
    if roll > 50:
        increment_points(username, wager, "+")
        return f"{username} rolled a {roll}! You've won {wager} points. You now have {points + wager} points."
    else:
        increment_points(username, wager, "-")
        return f"{username} rolled a {roll}! You've lost {wager} points, loser. You now have {points - wager} points."


def gamblestats(msg) -> str:
    """ Returns gamble stats for users.

    Potentially add ability to check other users' stats.
    """

    detailed = 'detailed' in msg.command_body
    user = get_user(msg.username)
    ret = ''
    if not msg.command_body:
        return f'You can type "!gamblestats playcount" or "!gamblestats points" to see your gambling stats! Add "detailed" at the end to see a breakdown.'
    if 'playcount' in msg.command_body:
        playcount_delta = user.times_won - user.times_lost
        stat1, stat2 = 'lost', 'won'
        if playcount_delta > 0:
            stat1, stat2 = 'won', 'lost'
        ret += f"{msg.username} has {stat1} {abs(playcount_delta)} more than they've {stat2}!"
        if detailed:
            percent = (user.times_won / (user.times_won + user.times_lost)) * 100
            ret += f" You have a {percent:.2f}% success rate, with a total of {user.times_won} times won and {user.times_lost} times lost."
    elif 'points' in msg.command_body:
        points_delta = user.points_won - user.points_lost
        stat1, stat2 = 'lost', 'won'
        if points_delta > 0:
            stat1, stat2 = 'won', 'lost'
        ret += f"{msg.username} has {stat1} {abs(points_delta)} points more than they've {stat2}."
        if detailed:
            ret += f" You've won {user.points_won} points and lost {user.points_lost} points total in your gambling addiction."
    return ret


def get_user(username) -> Points:
    """Returns a user db object from the username"""

    user = Points.get_or_create(name=username)
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


def close_db():
    db.close()


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
