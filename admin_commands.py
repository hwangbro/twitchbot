import api
import commands
import db

admin_commands = {
    'setgame': api.set_game,
    'settitle': api.set_title,
}

admin_commands_2 = {
    'setpoints': db.set_points,
}