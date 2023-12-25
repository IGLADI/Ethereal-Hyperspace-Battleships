from threading import Thread

import data
from database import Database
from ship import Ship
from utils import get_betted_amount
from location import Coordinate

_db = Database()


class Player:
    def __init__(self, discord_id):
        global _db
        ship_id = _db.player_ship_id(discord_id)
        money = _db.player_money(discord_id)
        x_pos, y_pos = _db.player_coordinates(discord_id)
        name = _db.player_name(discord_id)
        guild_name = _db.player_guild_name(discord_id)

        self._id = discord_id
        self._name = name
        self._guild_name = guild_name
        self._ship = Ship(ship_id)
        self._money = money

        self._x_pos = x_pos
        self._y_pos = y_pos

        self._on_message_reward_cooldown = False

        self._energy_thread = Thread(target=self.update_energy)
        self._energy_thread.daemon = True
        self._energy_thread.start()

        self._is_traveling = False
        self._is_mining = False
        # -1 = not in tutorial, 0 = in tutorial, 1 = tutorial finished
        self._tutorial = -1

        self._bonus_hit_chance = 0
        self._target: Player = None

    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, target):
        self._target = target

    @property
    def bonus_hit_chance(self):
        return self._bonus_hit_chance

    @bonus_hit_chance.setter
    def bonus_hit_chance(self, bonus_hit_chance):
        self._bonus_hit_chance = bonus_hit_chance
        if self._bonus_hit_chance > 20:
            self._bonus_hit_chance = 20

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def guild_name(self):
        return self._guild_name

    @property
    def money(self):
        betted_amount = get_betted_amount(self.id)
        return self._money - betted_amount

    @property
    def x_pos(self):
        return self._x_pos

    @property
    def y_pos(self):
        return self._y_pos

    @x_pos.setter
    def x_pos(self, x_pos):
        _db.player_set_x_pos(self.id, x_pos)
        self._x_pos = x_pos

    @y_pos.setter
    def y_pos(self, y_pos):
        global _db
        _db.player_set_y_pos(self.id, y_pos)
        self._y_pos = y_pos

    @property
    def ship(self):
        return self._ship

    @ship.setter
    def ship(self, ship):
        self._ship = ship

    @money.setter
    def money(self, amount):
        global _db
        self._money = amount if self._money >= 0 else 0
        _db.player_set_money(self.id, self._money)

    @property
    def on_message_reward_cooldown(self) -> bool:
        return self._on_message_reward_cooldown

    @on_message_reward_cooldown.setter
    def on_message_reward_cooldown(self, on_message_reward_cooldown: bool):
        self._on_message_reward_cooldown = on_message_reward_cooldown

    @property
    def is_traveling(self):
        return self._is_traveling

    @is_traveling.setter
    def is_traveling(self, is_traveling):
        self._is_traveling = is_traveling

    @property
    def tutorial(self):
        return self._tutorial

    @tutorial.setter
    def tutorial(self, int):
        self._tutorial = int

    # TODO make a secondary module like solar panels (slow but doesn't consume uranium=>players don't get stuck)
    def update_energy(self):
        while True:
            if self.ship.energy < 100:
                # generate solar energy
                self.ship.energy += self.ship.modules["EnergyGenerator"].generation
                # generate with energy generator
                if self.ship.modules["EnergyGenerator"].is_on:
                    # always use 1 uranium for now, will probably add a different rendement per level later on
                    uranium = self.ship.modules["Cargo"].resources.get("Uranium")
                    if uranium and uranium.amount >= 1:
                        self.ship.add_energy(self.ship.modules["EnergyGenerator"].generation)
                        uranium.amount -= 1
                asyncio.sleep(60)

    @classmethod
    def register(cls, discord_id, discord_name, player_class, guild_name):
        """Registers a new player in the database."""
        global _db
        _db.store_player(discord_id, discord_name, player_class, guild_name)
        Ship.store(discord_id)

    @classmethod
    def exists(cls, discord_id) -> bool:
        """Returns if a player exists with discord_id."""
        global _db
        return _db.player_exists(discord_id)

    @classmethod
    def get(cls, discord_id):
        """Gets a player from the players cache, if player is not found add it to the cache.
        Note: This assumes player with discord_id exists in the database."""
        if data.CACHE_DISABLED:
            return cls(discord_id)
        p = data.players.get(discord_id)
        if p is None:
            p = cls(discord_id)
            data.players[discord_id] = p
        return p

    # Travel Commands
    def travel(self, destination: Coordinate) -> int:
        """Travels to the given coordinates and returns distance."""

        old_pos = Coordinate(self.x_pos, self.y_pos)
        distance = int(old_pos.distance_to(destination))

        if distance > self.ship.modules["TravelModule"].max_distance:
            raise Exception("You can't travel that far! You need to upgrade your travel module.")

        def travel_thread():
            self.is_traveling = True
            while self._x_pos != destination.x or self._y_pos != destination.y:
                if self._x_pos < destination.x:
                    self._x_pos += 1
                elif self._x_pos > destination.x:
                    self._x_pos -= 1
                if self._y_pos < destination.y:
                    self._y_pos += 1
                elif self._y_pos > destination.y:
                    self._y_pos -= 1
                asyncio.sleep(1)
            _db.player_set_x_pos(self.id, self._x_pos)
            _db.player_set_y_pos(self.id, self._y_pos)
            self.is_traveling = False

        travel_thread_instance = Thread(target=travel_thread)
        travel_thread_instance.start()
        return distance

    def scan(self):
        """Returns a list of locations in a grid around the ship, depending on the radar module level"""
        scan_range = self.ship.modules["RadarModule"].radar_range // 2
        return _db.players_from_scan(
            x_pos=self.x_pos, y_pos=self.y_pos, distance=scan_range, excluded_player_discord_id=self.id
        )

    def long_scan(self):
        scan_range = self.ship.modules["RadarModule"].radar_range // 2
        locations = _db.location_from_scan(self.x_pos, self.y_pos, scan_range)
        # Tutorial space pirates
        if self._tutorial == 0:
            locations += [("Space pirates", 1, 0)]
            data.tutorials[self.id]._used_radar = True
        # Event locations
        if data.event_manager.events == {}:
            if (
                Coordinate(self.x_pos, self.y_pos).distance_to(
                    Coordinate(data.event_manager.events[1].x_pos, data.event_manager.events[1].y_pos)
                )
                <= 10
            ):
                locations += [
                    "Ruebñ's lost ship",
                    data.event_manager.events[1].x_pos,
                    data.event_manager.events[1].y_pos,
                ]
        return locations
