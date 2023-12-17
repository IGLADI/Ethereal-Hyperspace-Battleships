from ship import Ship
from utils import get_betted_amount
from threading import Thread
import time

import data

from database import Database

_db = Database()


# TODO when implementing the db, on load of the players call init with values (and put actual values as default values)
class Player:
    def __init__(self, id):
        self.id = id

        global _db
        self._money = _db.player_money(id)
        self._x_pos, self._y_pos = _db.player_coordinates(id)

        self._ship = Ship()
        self._energy_thread = Thread(target=self.update_energy)
        self._energy_thread.daemon = True
        self._energy_thread.start()

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

    @property
    def ship(self):
        return self._ship

    @money.setter
    def money(self, amount):
        global _db
        self._money = amount if self._money >= 0 else 0
        _db.player_set_money(self.id, self._money)
        _db.connection.commit()

    # TODO make a secondary module like solar panels (slow but doesn't consume uranium=>players don't get stuck)
    def update_energy(self):
        while True:
            if self.ship.energy < 100:
                # generate solar energy
                self.ship.add_energy(self.ship.modules[8].generation)
                # generate with energy generator
                if self.ship.modules[7].is_on:
                    # always use 1 uranium for now, will probably add a different rendement per level later on
                    for resource in self.ship.modules[5]._capacity:
                        if resource.name == "Uranium":
                            uranium_amount = resource.amount
                            break
                    if uranium_amount >= 1:
                        self.ship.add_energy(self.ship.modules[7].generation)
                        self._ship.remove_resource("Uranium", 1)
                time.sleep(60)

    def location_name(self) -> str:
        global _db
        return _db.player_location_name(self.id)

    @classmethod
    def commit(cls):
        global _db
        _db.connection.commit()

    @classmethod
    def register(cls, discord_id, discord_name, player_class):
        """Registers a new player in the database."""
        global _db
        counts = _db.guild_player_counts()
        next_guild = _db.next_guild(counts)
        _db.store_player(discord_id, discord_name, player_class, next_guild)
        _db.connection.commit()

    @classmethod
    def exists(cls, discord_id) -> bool:
        """Returns if a player exists with discord_id."""
        global _db
        return _db.player_exists(discord_id)

    @classmethod
    def get(cls, discord_id):
        """Gets a player from the players cache, if player is not found add it to the cache.
        Note: This assumes player with discord_id exists in the database."""
        p = data.players.get(discord_id)
        if p is None:
            p = cls(discord_id)
            data.players[discord_id] = p
        return p
