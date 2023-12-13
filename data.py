# TODO this is a temporary file to store data, will be replaced by a database/json file
class Guild:
    def __init__(self, name):
        self.name = name


race_games = {}
players = {}
guilds = [Guild("The Federation"), Guild("The Empire"), Guild("The Alliance"), Guild("The Independents")]
