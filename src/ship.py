from database import Database

from module import DEFAULT_MODULES

_db = Database()


class Ship:
    def __init__(self, ship_id):
        global _db
        module_ids = _db.ship_module_ids(ship_id)

        modules = {}
        for module_id in module_ids:
            type = _db.module_type(module_id)
            module = DEFAULT_MODULES.get(type)
            modules[type] = module(module_id)

        self.id = ship_id
        self._modules = modules
        # TODO make this in apart battery module
        self._energy = 100
        self._energy_capacity = 100

    @property
    def energy_capacity(self) -> int:
        return self._energy_capacity

    @property
    def energy(self) -> int:
        return self._energy

    @property
    def modules(self) -> dict:
        return self._modules

    @energy.setter
    def energy(self, energy):
        self._energy = energy

    @classmethod
    def store(cls, discord_id):
        """Stores a new ship with default modules."""
        global _db
        _db.store_ship(discord_id)

        ship_id = _db.player_ship_id(discord_id)
        for module in DEFAULT_MODULES.values():
            module.store(ship_id)
