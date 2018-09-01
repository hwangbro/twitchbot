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


def set_points(user, points):
	pts = read_points()
	pts[user] = points
	write_points(pts)


def add_points(user, points):
	pts = read_points()
	if user in pts:
		pts[user] += points
	else:
		pts[user] = points
	write_points(pts)


def get_points(user):
	pts = read_points()
	if user in pts:
		return pts[user]
	return 0


def gamble(username, wager):
	points = get_points(user)
	if wager > points:
		return
	if randint(1, 100) > 50:
		add_points(username, wager)
	else:
		pass #to do
