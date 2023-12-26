# TODO this is a temporary file to store data, will be replaced by a database/json file

race_games = {}
players = {}
planets = {}
tutorials = {}
event_manager = None

guild_names = ["The Federation", "The Empire", "The Alliance", "The Independents"]

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
    {"type": "text", "name": "events", "position": 2},
    {"type": "forum", "name": "questions", "position": 3},
    {"type": "voice", "name": "general", "position": 4},
]

RESOURCE_NAMES = ["rock", "copper", "silver", "gold", "uranium", "black matter"]
BUILDING_TYPES = [
    "repair station",
    "shop",
    "outpost",
    "factory",
    "mining station",
    "sace warp",
    "trading station",
    "casino",
]

# chances a player has to receive a reward when eligible
REWARD_ON_MESSAGE_CHANCE = 100
# seconds a player has to wait before he is eligible for message rewards
REWARD_ON_MESSAGE_COOLDOWN = 900
# Todo, set this wherever possible
GENERAL_NAME = "Ethereal Hyperspace Battleships General"

CACHE_DISABLED = False
