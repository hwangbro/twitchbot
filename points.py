import json

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