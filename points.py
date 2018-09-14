import json
from random import randint

def read_points() -> {str:int}:
	with open("points.json", "r") as p:
		return json.load(p)


def write_points(pts: {str:int}):
	with open("points.json", "w") as p:
		json.dump(pts, p, indent=4)


def update_viewers(usernames: [str]):
	pts = read_points()
	for user in usernames:
		if user in pts.keys():
			pts[user] += 1
		else:
			pts[user] = 1
	write_points(pts)


def set_points(msg: str) -> str:
	message = msg.split()
	if len(message) != 2:
		return "Incorrect format."
	try:
		user, pts2 = message
		points = int(pts2)
	except:
		return "Incorrect format."
	pts = read_points()
	pts[user] = points
	write_points(pts)
	return f"{user} now has {pts2} points"


def add_points(msg: str) -> str:
	message = msg.split()
	if len(message) != 2:
		return "Incorrect format."
	try:
		user, pts2 = message
		points = int(pts2)
	except:
		return "Incorrect format."
	pts = read_points()
	if user in pts:
		pts[user] += points
	else:
		pts[user] = points
	write_points(pts)
	return f"You have added {pts2} points to {user}"

def sub_points(msg: str) -> str:
	message = msg.split()
	if len(message) != 2:
		return "Incorrect format."
	try:
		user, pts2 = message
		points = int(pts2) * -1
	except:
		return "Incorrect format."
	pts = read_points()
	if user in pts:
		pts[user] += points
	else:
		pts[user] = points
	write_points(pts)
	return f"You have subtracted {pts2} points from {user}"


def get_points(user, user2) -> str:
	pts = read_points()
	if user2:
		if len(user2.split()) > 1:
			return "Incorrect username format, please try again nerd."
		if user2 not in pts:
			return user2 + " has no points."
		return "The loser " + user2 + " currently has " + str(pts[user2]) + " points."
	elif user in pts:
		return "You currently have " + str(pts[user]) + " points."
	return "Error."

def get_user_points(user):
	pts = read_points()
	if user in pts:
		return pts[user]
	return 0

def gamble(username, wager):
	points = get_user_points(username)
	roll = randint(1, 100)
	if wager > points:
		return "You don't have enough points to gamble."
	if roll > 50:
		add_points(username + " " + str(wager))
		return f"You rolled a {str(roll)}! You've won {wager} points."
	else:
		sub_points(username + " " + str(wager))
		return f"You rolled a {str(roll)}! You've lost {wager} points, loser."