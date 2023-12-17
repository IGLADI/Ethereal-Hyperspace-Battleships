# !!! IMPORTANT !!! ###########################################################
# for now functions that alter the table namely INSERT and UPDATE do not commit the change, because the changes will probably happen in bulk.

import mariadb
import json
import data


def get_connection():
    """Returns a connection to the database using credentials in config.json"""
    with open("config.json", "r") as f:
        data = json.load(f)
        db_data = data["database"]

    host = db_data["host"]
    user = db_data["user"]
    password = db_data["password"]
    database = db_data["database"]

    try:
        connection = mariadb.connect(
            host=host, user=user, password=password, port=3306, database=database
        )
        connection.autocommit = False
        return connection
    except mariadb.Error as e:
        print("Error connecting to MariaDB:", e)
        return None


def get_next_guild(results):
    """Where results is a tuple with guild_name, player_count"""
    results_names = [result[0] for result in results]

    for guild_name in data.guild_names:
        if guild_name not in results_names:
            return guild_name

    return min(results, key=lambda x: x[1])[0]


class Database:
    """Database class for interacting with the mariadb database.  Has usefule queries to aid gameplay."""

    def __init__(self):
        "creates a connection and cursor object for the class"
        self.connection = get_connection()
        self.cursor = self.connection.cursor()

    def get_results(self, statement, values=None) -> list:
        """Runs a SQL query and returns the tuple(s) of results in cursor"""
        self.cursor.execute(statement, values)
        self.connection.commit()
        return [row for row in self.cursor]

    def get_guild_player_counts(self):
        """Get the name of the guild with lowest player count"""
        statement = """
        SELECT g.name, COUNT(1) FROM players p
        JOIN guilds g ON g.guild_id = p.guild_id
        GROUP BY g.guild_id;
        """
        results = self.get_results(statement)
        return results

    # We assume this happens after player has chosen main guild
    def store_player(self, discord_id, discord_name, player_class, guild_name):
        """Creates a new player in the database with a guild name.  The coordinates of the planet of the main guild are used as the players starting coordinates."""
        statement = """
        INSERT INTO `players` (`discord_id`, `discord_name`, `class`, `guild_id`, `x_pos`, `y_pos`)
        SELECT ?, ?, ?, g.guild_id, p.location_x_pos, p.location_y_pos
        FROM guilds g
        JOIN planets p ON g.planet_id = p.planet_id
        WHERE g.name = ?;
        """
        self.cursor.execute(
            statement, (discord_id, discord_name, player_class, guild_name)
        )

    def player_exists(self, discord_id) -> bool:
        """Checks if a player exists in the database."""
        statement = """
        SELECT 1 FROM players p
        WHERE p.discord_id = ?"""
        self.cursor.execute(statement, (discord_id,))
        self.connection.commit()
        return self.cursor.rowcount != 0

    def player_location_name(self, discord_id) -> str:
        """Retunrs the location name of where the player is located."""
        statement = """
        SELECT l.name FROM locations l
        JOIN players p ON
            p.x_pos = l.location_x_pos AND
            p.y_pos = l.location_y_pos
        WHERE p.discord_id = ?;
        """
        results = self.get_results(statement, (discord_id,))
        return results[0][0] if results else None

    def player_coordinates(self, discord_id) -> tuple:
        """Returns the coordinates of the players as a tuple."""
        statement = """
        SELECT p.x_pos, p.y_pos FROM players p
        WHERE p.discord_id = ?;
        """
        results = self.get_results(statement, (discord_id,))
        return results[0] if results else None

    def get_player_money(self, discord_id) -> int:
        """Returns the money of the player as an int."""
        statement = """
        SELECT p.money FROM players p
        WHERE p.discord_id = ?;
        """
        results = self.get_results(statement, (discord_id,))
        money = results[0][0] if results else None
        return money

    def player_change_money(self, discord_id, amount):
        """Change the balance of a player."""
        statement = """
        UPDATE players SET money = money + ?
        WHERE discord_id = ?"""
        self.cursor.execute(statement, (amount, discord_id))
