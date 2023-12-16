# TODO this is a temporary file to store data, will be replaced by a database/json file
class Guild:
    def __init__(self, name):
        self.name = name


race_games = {}
players = {}
planets = {}
guilds = [Guild("The Federation"), Guild("The Empire"), Guild("The Alliance"), Guild("The Independents")]

guild_channels = [
    {"type": "text", "name": "announcements"},
    {"type": "text", "name": "general"},
    {"type": "text", "name": "off-topic"},
    {"type": "forum", "name": "guides"},
    {"type": "voice", "name": "quarters"},
    {"type": "stage", "name": "meeting room"},
]

general_channels = [
    {"type": "text", "name": "general", "position": 1},
    {"type": "forum", "name": "questions", "position": 2},
    {"type": "voice", "name": "general", "position": 3},
]
