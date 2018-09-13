import api
import commands
import db
import points

admin_commands = {
    'setgame': api.set_game,
    'settitle': api.set_title,
    'addpoints': points.add_points,
    'setpoints': points.set_points,
}

admin_commands_2 = {
    'setpoints': db.set_points,
}