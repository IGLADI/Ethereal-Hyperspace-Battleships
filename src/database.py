import mariadb
import json
import sys


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
        connection = mariadb.connect(host=host, user=user, password=password, port=3306, database=database)
        connection.autocommit = True
        return connection
    except mariadb.Error as e:
        print("Error connecting to MariaDB:", e)
        sys.exit(1)


class Database:
    """Database class for interacting with the mariadb database.  Has usefule queries to aid gameplay."""

    def __init__(self):
        "creates a connection and cursor object for the class"
        self._connection = get_connection()
        self._cursor = self._connection.cursor()

    # utils ###################################################################
    def get_results(self, statement, values=None) -> list:
        """Returns result of query."""
        self._cursor.execute(statement, values)
        return list(self._cursor)

    def get_only_result(self, statement, values=None):
        """get_results but returns the only result."""
        results = self.get_results(statement, values)
        return results[0][0] if results else None

    # player ##################################################################
    def player_exists(self, discord_id) -> bool:
        """Checks if a player exists in the database."""
        self._cursor.execute(
            """
            SELECT 1 FROM players
            WHERE discord_id = ?
            """,
            (discord_id,),
        )
        return self._cursor.rowcount != 0

    def player_location_name(self, discord_id) -> str:
        """Retunrs the location name of where the player is located."""
        return self.get_only_result(
            """
            SELECT l.name FROM locations l
            JOIN players p ON
                p.x_pos = l.location_x_pos AND
                p.y_pos = l.location_y_pos
            WHERE p.discord_id = ?
            """,
            (discord_id,),
        )

    def player_coordinates(self, discord_id) -> tuple:
        """Returns the coordinates of the players as a tuple."""
        results = self.get_results(
            """
            SELECT x_pos, y_pos FROM players
            WHERE discord_id = ?
            """,
            (discord_id,),
        )
        return results[0] if results else None

    def player_money(self, discord_id) -> int:
        """Returns the money of the player as an int."""
        return self.get_only_result(
            """
            SELECT money FROM players
            WHERE discord_id = ?
            """,
            (discord_id,),
        )

    def player_set_money(self, discord_id, amount):
        """Set the balance of a player."""
        self._cursor.execute(
            """
            UPDATE players SET money = ?
            WHERE discord_id = ?
            """,
            (amount, discord_id),
        )

    def player_name(self, discord_id) -> int:
        """Return ship_id for player_id"""
        return self.get_only_result(
            """
            SELECT discord_name FROM players
            WHERE discord_id = ?
            """,
            (discord_id,),
        )

    def player_ship_id(self, discord_id) -> int:
        """Return ship_id for player_id"""
        return self.get_only_result(
            """
            SELECT ship_id FROM ships s
            JOIN players p ON p.player_id = s.player_id
            WHERE p.discord_id = ?
            """,
            (discord_id,),
        )

    def player_set_x_pos(self, discord_id, x_pos) -> int:
        """Set x_pos for player id"""
        self._cursor.execute(
            """
            UPDATE players SET x_pos = ?
            WHERE discord_id = ?
            """,
            (x_pos, discord_id),
        )

    def player_set_y_pos(self, discord_id, y_pos) -> int:
        """Set y_pos for player id"""
        self._cursor.execute(
            """
            UPDATE players SET y_pos = ?
            WHERE discord_id = ?
            """,
            (y_pos, discord_id),
        )

    def player_from_scan(self, x_pos, y_pos, distance, excluded_player_discord_id) -> int:
        """Returns the player in a certain distance."""
        statement = """
        SELECT discord_name, x_pos, y_pos FROM players
        WHERE x_pos BETWEEN ? AND ? AND y_pos BETWEEN ? AND ?
        AND discord_id <> ?
        """
        results = self.get_results(
            statement,
            (x_pos - distance, x_pos + distance, y_pos - distance, y_pos + distance, excluded_player_discord_id),
        )
        return results if results else []

    # location ################################################################
    def location_from_scan(self, x_pos, y_pos, distance) -> str:
        """Returns the location name from coordinates in a certain distance."""
        statement = """
        SELECT name, location_x_pos, location_y_pos FROM locations
        WHERE location_x_pos BETWEEN ? AND ? AND location_y_pos BETWEEN ? AND ?
        """
        results = self.get_results(statement, (x_pos - distance, x_pos + distance, y_pos - distance, y_pos + distance))
        return results if results else []

    def location_from_coordinates(self, x_pos, y_pos) -> str:
        """Returns the location name from coordinates."""
        statement = """
        SELECT name FROM locations
        WHERE location_x_pos = ? AND location_y_pos = ?
        """
        results = self.get_results(statement, (x_pos, y_pos))
        return results[0][0] if results else None

    def location_image(self, x_pos, y_pos) -> str:
        """Returns the location image from coordinates."""
        statement = """
        SELECT image, name FROM locations
        WHERE location_x_pos = ? AND location_y_pos = ?
        """
        results = self.get_results(statement, (x_pos, y_pos))
        return results if results else []

    def set_location_image(self, x_pos, y_pos, image):
        """Set the location image from coordinates."""
        self._cursor.execute(
            """
            UPDATE locations SET image = ?
            WHERE location_x_pos = ? AND location_y_pos = ?
            """,
            (image, x_pos, y_pos),
        )

    # fuel ####################################################################
    def fuel_module_fuel(self, module_id) -> int:
        """Return fuel in a fuel module by module_id"""
        return self.get_only_result(
            """
            SELECT fuel FROM fuel_modules
            WHERE module_id = ?
            """,
            (module_id,),
        )

    def fuel_module_set_fuel(self, module_id: int, fuel: int):
        """Set fuel in fuel_module."""
        self._cursor.execute(
            """
            UPDATE fuel_modules SET fuel = ?
            WHERE module_id = ?
            """,
            (fuel, module_id),
        )

    # ship ####################################################################
    def ship_module_ids(self, ship_id) -> list:
        """Returns a list of module_ids."""
        statement = """
        SELECT module_id FROM modules
        WHERE ship_id = ?
        """
        results = self.get_results(statement, (ship_id,))
        ids = [result[0] for result in results]
        return ids

    # module ##################################################################
    def module_type(self, module_id) -> str:
        """Return the module type for a module_id."""
        return self.get_only_result(
            """
            SELECT type FROM modules
            WHERE module_id = ?
            """,
            (module_id,),
        )

    def module_ship_id(self, module_id) -> int:
        """Return ship_id for module"""
        return self.get_only_result(
            """
        SELECT ship_id FROM modules
        WHERE module_id = ?
        """,
            (module_id,),
        )

    def module_level(self, module_id) -> int:
        """Return module level"""
        return self.get_only_result(
            """
            SELECT level FROM modules
            WHERE module_id = ?
            """,
            (module_id,),
        )

    def module_set_level(self, module_id, module_level):
        self._cursor.execute(
            """
            UPDATE modules SET level = ?
            WHERE module_id = ?
            """,
            (module_level, module_id),
        )

    # item ####################################################################
    def item_type(self, item_id) -> int:
        """Return amount for item_id."""
        return self.get_only_result(
            """
            SELECT type FROM items
            WHERE item_id = ?
            """,
            (item_id,),
        )

    def item_amount(self, item_id) -> int:
        """Return amount for item_id."""
        return self.get_only_result(
            """
            SELECT amount FROM items
            WHERE item_id = ?
            """,
            (item_id,),
        )

    def item_name(self, item_id) -> str:
        """Return amount for item_id."""
        return self.get_only_result(
            """
            SELECT name FROM items
            WHERE item_id = ?
            """,
            (item_id,),
        )

    def item_set_amount(self, item_id, amount):
        self._cursor.execute(
            """
            UPDATE items SET amount = ?
            WHERE item_id = ?
            """,
            (amount, item_id),
        )

    def item_delete(self, item_id):
        """Delete an item by item id."""
        self._cursor.execute(
            """
            DELETE FROM contributions
            WHERE item_id = ?
            """,
            (item_id,),
        )
        self._cursor.execute(
            """
            DELETE FROM items
            WHERE item_id = ?
            """,
            (item_id,),
        )

    # contribution ############################################################
    def contribution_exists(self, building_id, item_name: str) -> int:
        """Check if an item is in contributions."""
        return self.get_only_result(
            """
            SELECT c.item_id FROM contributions c
            JOIN items i ON i.item_id = c.item_id
            WHERE c.building_id = ? AND i.name = ?
            """,
            (building_id, item_name),
        )

    # cargo ###################################################################
    def cargo_resource_ids(self, cargo_module_id) -> list:
        """Returns a list of item ids."""
        statement = """
        SELECT item_id FROM items
        WHERE cargo_module_id = ? AND type = 'resource'
        """
        results = self.get_results(statement, (cargo_module_id,))
        ids = [result[0] for result in results]
        return ids

    def cargo_module_id(self, module_id):
        """Return cargo id by module id."""
        return self.get_only_result(
            """
            SELECT cargo_module_id FROM cargo_modules
            WHERE module_id = ?
            """,
            (module_id,),
        )

    # Storing commands ########################################################

    def store_item(self, name, item_type, cargo_module_id=None, amount=1) -> int:
        """Store an item to a cargo_module_id."""
        return self.get_only_result(
            """
            INSERT INTO items (name, type, cargo_module_id, amount)
            VALUES (?, ?, ?, ?)
            RETURNING item_id
            """,
            (name, item_type, cargo_module_id, amount),
        )

    def store_contribution(self, item_id, building_id) -> int:
        return self.get_only_result(
            """
            INSERT INTO contributions
            VALUES (?, ?)
            RETURNING item_id
            """,
            (building_id, item_id),
        )

    # We assume this happens after player has chosen main guild
    def store_player(self, discord_id, discord_name, player_class, guild_name) -> int:
        """Creates a new player in the database with a guild name.  The coordinates of the planet of the main guild are used as the players starting coordinates."""
        return self.get_only_result(
            """
            INSERT INTO `players` (`discord_id`, `discord_name`, `class`, `guild_id`, `x_pos`, `y_pos`)
            SELECT ?, ?, ?, g.guild_id, p.location_x_pos, p.location_y_pos
            FROM guilds g
            JOIN planets p ON g.planet_id = p.planet_id
            WHERE g.name = ?
            RETURNING player_id
            """,
            (discord_id, discord_name, player_class, guild_name),
        )

    def store_building(self, building_type, planet_id) -> int:
        return self.get_only_result(
            """
            INSERT INTO buildings (type, planet_id)
            VALUES (?, ?)
            RETURNING building_id
            """,
            (building_type, planet_id),
        )

    def store_ship(self, discord_id) -> int:
        """Store a ship for a player."""
        return self.get_only_result(
            """
            INSERT INTO ships (player_id)
            SELECT player_id FROM players
            WHERE discord_id = ?
            RETURNING ship_id
            """,
            (discord_id,),
        )

    def store_module(self, ship_id, module_type) -> int:
        """Store module with a ship id."""
        return self.get_only_result(
            """
            INSERT INTO modules (`type`, `ship_id`)
            VALUES (?, ?)
            RETURNING module_id
            """,
            (module_type, ship_id),
        )

    def store_cargo_module(self, ship_id) -> int:
        """Store a cargo module with a ship id."""
        self.store_module(ship_id, "Cargo")
        return self.get_only_result(
            """
            INSERT INTO cargo_modules (`module_id`) 
            SELECT module_id FROM modules
            WHERE ship_id = ? AND type = 'Cargo'
            RETURNING cargo_module_id
            """,
            (ship_id,),
        )

    def store_fuel_module(self, ship_id) -> int:
        """Store a fuel module with a ship id."""
        self.store_module(ship_id, "Fuel")
        return self.get_only_result(
            """
            INSERT INTO fuel_modules (`module_id`)
            SELECT module_id FROM modules
            WHERE ship_id = ? AND type = 'Fuel'
            RETURNING fuel_module_id
            """,
            (ship_id,),
        )

    def store_bug_report(self, discord_id, bug_report):
        """Store a bug report."""
        self._cursor.execute(
            """
            INSERT INTO reports (discord_id, content)
            VALUES (?, ?)
            """,
            (discord_id, bug_report),
        )
