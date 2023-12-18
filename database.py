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
        connection.autocommit = True
        return connection
    except mariadb.Error as e:
        print("Error connecting to MariaDB:", e)
        return None


class Database:
    """Database class for interacting with the mariadb database.  Has usefule queries to aid gameplay."""

    def __init__(self):
        "creates a connection and cursor object for the class"
        self._connection = get_connection()
        self._cursor = self._connection.cursor()

    def get_results(self, statement, values=None) -> list:
        """Returns result of query."""
        self._cursor.execute(statement, values)
        return [row for row in self._cursor]

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
        self._cursor.execute(
            statement, (discord_id, discord_name, player_class, guild_name)
        )

    def player_exists(self, discord_id) -> bool:
        """Checks if a player exists in the database."""
        statement = """
        SELECT 1 FROM players p
        WHERE p.discord_id = ?"""
        self._cursor.execute(statement, (discord_id,))
        return self._cursor.rowcount != 0

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

    def player_money(self, discord_id) -> int:
        """Returns the money of the player as an int."""
        statement = """
        SELECT p.money FROM players p
        WHERE p.discord_id = ?;
        """
        results = self.get_results(statement, (discord_id,))
        money = results[0][0] if results else None
        return money

    def player_set_money(self, discord_id, amount):
        """Set the balance of a player."""
        statement = """
        UPDATE players SET money = ?
        WHERE discord_id = ?"""
        self._cursor.execute(statement, (amount, discord_id))

    def store_ship(self, discord_id):
        """Store a ship for a player."""
        statement = """
        INSERT INTO ships (player_id)
        SELECT player_id FROM players
        WHERE discord_id = ?
        """
        self._cursor.execute(statement, (discord_id,))

    def player_ship_id(self, discord_id) -> int:
        """Return ship_id for player_id"""
        statement = """
        SELECT ship_id FROM ships s
        JOIN players p ON p.player_id = s.player_id
        WHERE p.discord_id = ?
        """
        results = self.get_results(statement, (discord_id,))
        if len(results):
            return results[0][0]
        return None

    def store_module(self, ship_id, module_type):
        """Store module with a ship id."""
        statement = """
        INSERT INTO modules (`type`, `ship_id`) VALUES (?, ?)
        """
        self._cursor.execute(statement, (module_type, ship_id))

    def store_cargo_module(self, ship_id):
        """Store a cargo module with a ship id."""
        statement = """
        INSERT INTO cargo_modules (`module_id`) 
        SELECT m.module_id FROM modules m
        WHERE m.ship_id = ? AND m.type = 'Cargo'
        """
        self.store_module(ship_id, "Cargo")
        self._cursor.execute(statement, (ship_id,))

    def store_fuel_module(self, ship_id):
        """Store a fuel module with a ship id."""
        statement = """
        INSERT INTO fuel_modules (`module_id`)
        SELECT m.module_id FROM modules m
        WHERE m.ship_id = ? AND m.type = 'Fuel'
        """
        self.store_module(ship_id, "Fuel")
        self._cursor.execute(statement, (ship_id,))

    def fuel_module_fuel(self, module_id) -> int:
        """Return fuel in a fuel module by module_id"""
        statement = """
        SELECT fuel FROM fuel_modules
        WHERE module_id = ?
        """
        results = self.get_results(statement, (module_id,))
        return results[0][0] if results else None

    def ship_module_ids(self, ship_id) -> list:
        """Returns a list of module_ids."""
        statement = """
        SELECT module_id FROM modules
        WHERE ship_id = ?
        """
        results = self.get_results(statement, (ship_id,))
        ids = [result[0] for result in results]
        return ids

    def module_type(self, module_id) -> str:
        """Return the module type for a module_id."""
        statement = """
        SELECT type FROM modules
        WHERE module_id = ?
        """
        results = self.get_results(statement, (module_id,))
        return results[0][0] if results else None

    def module_ship_id(self, module_id) -> int:
        statement = """
        SELECT ship_id FROM modules
        WHERE module_id = ?
        """
        results = self.get_results(statement, (module_id,))
        return results[0][0] if results else None

    def module_level(self, module_id) -> int:
        statement = """
        SELECT level FROM modules
        WHERE module_id = ?
        """
        results = self.get_results(statement, (module_id,))
        return results[0][0] if results else None

    def module_set_level(self, module_id, module_level):
        statement = """
        UPDATE modules SET level = ?
        WHERE module_id = ?
        """
        self._cursor.execute(statement, (module_level, module_id))
