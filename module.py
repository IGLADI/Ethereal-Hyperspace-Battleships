from database import Database
from item import Resource


_db = Database()


# The comments show the properties of each module at each level. These can be changed as we need to balance the game.
class Module:
    def __init__(self, module_id, name, description, max_level, cost):
        global _db
        level = _db.module_level(module_id)

        self._id = module_id
        self._name = name
        self._description = description
        self._level = level
        self._max_level = max_level
        self._cost = cost

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    @property
    def level(self):
        return self._level

    @property
    def max_level(self):
        return self._max_level

    @property
    def cost(self):
        return self._cost

    @level.setter
    def level(self, level):
        global _db
        if level > self.max_level:
            raise ValueError("Module is already at max level")
        self._level = level
        _db.module_set_level(self.id, level)

    def upgrade(self, cargo):
        """Uses resources in cargo of player to upgrade module."""
        if self._level == self._max_level:
            raise Exception("Module is already at max level.")

        if not self.can_upgrade(cargo):
            raise Exception("Not enough resources to upgrade.")

        for cost in self._cost:
            resource_name = cost["resource"]
            required_amount = cost["amount"]

            if required_amount == 0:
                continue

            resource = cargo.resources.get(resource_name)
            if not resource:
                continue

            resource.amount -= required_amount
            if resource.amount == 0:
                cargo.resources.pop(resource_name)

        print("hehe")
        self.level += 1

    def can_upgrade(self, cargo) -> bool:
        """Utility function to check if a player has enough resources to upgrade a module."""
        for cost in self._cost:
            resource_name = cost["resource"]
            required_amount = cost["amount"]

            if required_amount == 0:
                continue

            resource = cargo.resources.get(resource_name)
            if not resource:
                return False
            if resource.amount < required_amount:
                return False

        return True

    def __str__(self):
        cost_str = "".join(
            f"\n   - {cost['resource']}: {cost['amount']}" for cost in self._cost
        )
        if self._level == self._max_level:
            return (
                f" - **Name: {self._name}**\n"
                f" - Description: {self._description}\n"
                f" - Level: {self._level}/{self._max_level}\n"
                f" - Upgrade Cost: MAX LEVEL\n"
            )
        return (
            f" - **Name: {self._name}**\n"
            f" - Description: {self._description}\n"
            f" - Level: {self._level}/{self._max_level}\n"
            f" - Upgrade Cost: {cost_str}\n"
        )

    @classmethod
    def store(cls, ship_id):
        global _db
        _db.store_module(ship_id, cls.__name__)


class TravelModule(Module):
    def __init__(self, module_id):
        super().__init__(
            module_id,
            "Travel Module",
            "Increases the distance the ship can travel.",
            6,
            [
                {"resource": "rock", "amount": 0},
                {"resource": "copper", "amount": 200},
                {"resource": "silver", "amount": 0},
                {"resource": "gold", "amount": 0},
            ],
        )
        self._max_distance = 1000

    @property
    def max_distance(self):
        return self._max_distance

    # max_distance levels:  1000,   1500,   1900,   2200,     2400,     2500
    # rock cost levels:    100,    300,    900,    2700,     8100,     24300
    # copper cost levels:   200,    200,    300,    400,      500,      600
    # silver cost levels:   0,      200,    300,    400,      500,      600
    # gold cost levels:     0,      200,    300,    400,      500,      600
    def upgrade(self, cargo_player):
        super().upgrade(cargo_player)
        upgrade_amount = 500 - (100 * (self.level - 2))
        self._max_distance += upgrade_amount
        if self.level == 2:
            for i in range(2, 4):
                self._cost[i]["amount"] = 200
        else:
            for i in range(1, 4):
                self._cost[i]["amount"] += 100

    def __str__(self):
        return f"{super().__str__()} - Max Distance: {self._max_distance} lightyears\n"


class MiningModule(Module):
    def __init__(self, module_id):
        super().__init__(
            module_id,
            "Mining Module",
            "Increases the amount of resources the ship can mine.",
            5,
            [
                {"resource": "rock", "amount": 0},
                {"resource": "copper", "amount": 150},
                {"resource": "silver", "amount": 150},
                {"resource": "gold", "amount": 150},
            ],
        )
        self._mining_bonus = 100

    @property
    def mining_bonus(self):
        return self._mining_bonus

    # mining_bonus levels:  100,    101,    103,    105,      110
    # rock cost levels:    100,    300,    900,    2700,     8100
    # copper cost levels:   0,      200,    300,    400,      500
    # silver cost levels:   200,    200,    300,    400,      500
    # gold cost levels:     0,      200,    300,    400,      500
    def upgrade(self, cargo_player):
        super().upgrade(cargo_player)

        if self.level == 2:
            self._mining_bonus += 1
        elif self.level == 3 or self.level == 4:
            self._mining_bonus += 2
        elif self.level == 5:
            self._mining_bonus += 5
        if self.level == 2:
            for i in [1, 3]:
                self._cost[i]["amount"] = 200
        else:
            for i in range(1, 4):
                self._cost[i]["amount"] += 100

    def __str__(self):
        return f"{super().__str__()} - Mining Bonus: {self._mining_bonus}%\n"


class Cargo(Module):
    def __init__(self, module_id):
        super().__init__(
            module_id,
            "Cargo",
            "Increases the amount of cargo the ship can hold.",
            6,
            [
                {"resource": "rock", "amount": 0},
                {"resource": "copper", "amount": 150},
                {"resource": "silver", "amount": 150},
                {"resource": "gold", "amount": 150},
            ],
        )
        global _db
        cargo_module_id = _db.cargo_module_id(module_id)
        item_ids = _db.cargo_resource_ids(cargo_module_id)

        self.cargo_id = cargo_module_id
        self._capacity = 0
        self._max_capacity = 600
        self._resources = {}

        for item_id in item_ids:
            name = _db.item_name(item_id)
            self._resources[name] = Resource(item_id)
            self._capacity += self._resources[name].amount

    @property
    def capacity(self):
        return self._capacity

    @property
    def max_capacity(self):
        return self._max_capacity

    @property
    def resources(self):
        return self._resources

    @capacity.setter
    def capacity(self, capacity: int):
        if self._capacity + capacity > self.max_capacity:
            raise ValueError("Storage exceeded")
        self._capacity = capacity

    # max_capacity levels:  300,    400,    500,    600,      800,      1000
    # rock cost levels:    100,    300,    900,    2700,     8100,     24300
    # copper cost levels:   0       200,    300,    400,      500,      600
    # silver cost levels:   0,      200,    300,    400,      500,      600
    # gold cost levels:     200,    200,    300,    400,      500,      600
    def upgrade(self, cargo_player):
        super().upgrade(cargo_player)
        if self.level < 5:
            self._max_capacity += 100
        else:
            self._max_capacity += 200
        if self.level == 2:
            for i in range(1, 3):
                self._cost[i]["amount"] = 200
        else:
            for i in range(1, 4):
                self._cost[i]["amount"] += 100

    def add_resource(self, resource_name, amount):
        """Adds a resource to the module, creates a new one or stack with existing resource."""
        resource = self.resources.get(resource_name)
        if resource:
            resource.amount += amount
            self._capacity += amount
            return

        resource_id = Resource.store(
            name=resource_name, amount=amount, cargo_module_id=self.cargo_id
        )
        resource = Resource(resource_id)
        self._resources[resource_name] = resource
        self._capacity += resource.amount

    def __str__(self):
        resources_str = "".join(
            f"\n   - {resource}"
            for resource in self.resources.values()
            if resource.amount > 0
        )
        return f"{super().__str__()} - Capacity: {resources_str} \n - Storage: {self.capacity}/{self._max_capacity} tons\n"

    @classmethod
    def store(cls, ship_id) -> int:
        global _db
        return _db.store_cargo_module(ship_id)


class Canon(Module):
    def __init__(self, module_id):
        super().__init__(
            module_id,
            "Canon",
            "Increases the ship's attack damage.",
            5,
            [
                {"resource": "rock", "amount": 0},
                {"resource": "copper", "amount": 150},
                {"resource": "silver", "amount": 150},
                {"resource": "gold", "amount": 150},
            ],
        )

        self._strength = 100

    @property
    def strength(self):
        return self._strength

    # strength levels:      100,    110,    130,    145,    150
    # rock cost levels:    200,    600,    1200,   3600,   10800
    # copper cost levels:   150,    300,    450,    600,    750
    # silver cost levels:   150,    300,    450,    600,    750
    # gold cost levels:     150,    300,    450,    600,    750
    def upgrade(self, cargo_player):
        super().upgrade(cargo_player)
        if self.level == 2:
            self._strength += 10
        elif self.level == 3:
            self._strength += 20
        elif self.level == 4:
            self._strength += 15
        elif self.level == 5:
            self._strength += 5
        for i in range(1, 4):
            self._cost[i]["amount"] += 150

    def __str__(self):
        return f"{super().__str__()} - Strength: {self._strength} firepower\n"


class Shield(Module):
    def __init__(self, module_id):
        super().__init__(
            module_id,
            "Shield",
            "Increases the ship's defense.",
            5,
            [
                {"resource": "rock", "amount": 0},
                {"resource": "copper", "amount": 150},
                {"resource": "silver", "amount": 150},
                {"resource": "gold", "amount": 150},
            ],
        )
        self._defense = 100

    @property
    def defense(self):
        return self._defense

    # defense levels:       100,    110,    130,    145,    150
    # rock cost levels:    200,    600,    1200,   3600,   10800
    # copper cost levels:   150,    300,    450,    600,    750
    # silver cost levels:   150,    300,    450,    600,    750
    # gold cost levels:     150,    300,    450,    600,    750
    def upgrade(self, cargo_player):
        super().upgrade(cargo_player)
        if self.level == 2:
            self._defense += 10
        elif self.level == 3:
            self._defense += 20
        elif self.level == 4:
            self._defense += 15
        elif self.level == 5:
            self._defense += 5
        for i in range(1, 4):
            self._cost[i]["amount"] += 150

    def __str__(self):
        return f"{super().__str__()} - Defense: {self._defense} armor\n"


class Fuel(Module):
    def __init__(self, module_id):
        super().__init__(
            module_id,
            "Fuel",
            "Holds the ship's fuel.",
            1,
            [
                {"resource": "rock", "amount": 0},
                {"resource": "copper", "amount": 0},
                {"resource": "silver", "amount": 0},
                {"resource": "gold", "amount": 0},
            ],
        )
        global _db
        fuel = _db.fuel_module_fuel(module_id)

        self._fuel = fuel

    @property
    def fuel(self):
        return self._fuel

    @fuel.setter
    def fuel(self, fuel):
        global _db
        _db.fuel_module_set_fuel(module_id=self.id, fuel=fuel)
        self._fuel = fuel

    def upgrade(self, cargo_player):
        super().upgrade(cargo_player)

    def __str__(self):
        return f"{super().__str__()} - Current Fuel: {self._fuel}%\n"

    @classmethod
    def store(cls, ship_id):
        global _db
        _db.store_fuel_module(ship_id)


class Radar(Module):
    def __init__(self, module_id):
        super().__init__(
            module_id,
            "Radar",
            "Increases the ship's radar range.",
            7,
            [
                {"resource": "rock", "amount": 0},
                {"resource": "copper", "amount": 50},
                {"resource": "silver", "amount": 50},
                {"resource": "gold", "amount": 50},
            ],
        )
        self._radar_range = 50

    @property
    def radar_range(self):
        return self._radar_range

    # radar_range levels:   50,     60,     70,     80,     90,     95,     100
    # rock cost levels:    500,    1000,   2000,   4000,   8000,   16000,  32000
    # copper cost levels:   50,     200,    350,    500,    650,    800,    950
    # silver cost levels:   50,     200,    350,    500,    650,    800,    950
    # gold cost levels:     50,     200,    350,    500,    650,    800,    950
    def upgrade(self, cargo_player):
        super().upgrade(cargo_player)
        if self.level < 6:
            self._radar_range += 10
        else:
            self._radar_range += 5
        for i in range(1, 4):
            self._cost[i]["amount"] += 150

    def __str__(self):
        return f"{super().__str__()} - Radar Range: {self._radar_range} lightyears\n"


# generation = amount / minute
class EnergyGenerator(Module):
    def __init__(self, module_id):
        super().__init__(
            module_id,
            "Energy Generator",
            "Increases the ship's energy generation.",
            7,
            [
                {"resource": "rock", "amount": 0},
                {"resource": "copper", "amount": 50},
                {"resource": "silver", "amount": 50},
                {"resource": "gold", "amount": 50},
            ],
        )
        self._generation = 10
        self._is_on = True
        self.booting = False

    @property
    def generation(self):
        return self._generation

    @property
    def is_on(self):
        return self._is_on

    # generation levels:    10,     20,     30,     50,     70,     100,    130
    # rock cost levels:    1000,   2000,   4000,   8000,   16000,  32000,  64000
    # copper cost levels:   50,     200,    350,    500,    650,    800,    950
    # silver cost levels:   50,     200,    350,    500,    650,    800,    950
    # gold cost levels:     50,     200,    350,    500,    650,    800,    950
    def upgrade(self, cargo_player):
        super().upgrade(cargo_player)
        if self.level == 2 or self.level == 3:
            self._generation += 10
        elif self.level == 4 or self.level == 5:
            self._generation += 20
        else:
            self._generation += 30
        for i in range(1, 4):
            self._cost[i]["amount"] += 150

    def __str__(self):
        return f"{super().__str__()} - Generation: {self._generation} per minute\n"

    def turn_on(self):
        self._is_on = True

    def turn_off(self):
        self._is_on = False


class SolarPanel(Module):
    def __init__(self, module_id):
        super().__init__(
            module_id,
            "Solar Panel",
            "Increases the ship's energy generation.",
            7,
            [
                {"resource": "rock", "amount": 0},
                {"resource": "copper", "amount": 50},
                {"resource": "silver", "amount": 50},
                {"resource": "gold", "amount": 50},
            ],
        )
        self._generation = 1

    @property
    def generation(self):
        return self._generation

    # generation levels:    1,      2,      3,      5,      7,      10,     13
    # rock cost levels:    1000,   2000,   4000,   8000,   16000,  32000,  64000
    # copper cost levels:   50,     200,    350,    500,    650,    800,    950
    # silver cost levels:   50,     200,    350,    500,    650,    800,    950
    # gold cost levels:     50,     200,    350,    500,    650,    800,    950
    def upgrade(self, cargo_player):
        super().upgrade(cargo_player)
        if self.level == 2 or self.level == 3:
            self._generation += 1
        elif self.level == 4 or self.level == 5:
            self._generation += 2
        else:
            self._generation += 3
        for i in range(1, 4):
            self._cost[i]["amount"] += 150

    def __str__(self):
        return f"{super().__str__()} - Generation: {self._generation} per minute\n"


DEFAULT_MODULES = {
    "SolarPanel": SolarPanel,
    "TravelModule": TravelModule,
    "MiningModule": MiningModule,
    "Canon": Canon,
    "Shield": Shield,
    "Fuel": Fuel,
    "Cargo": Cargo,
    "Radar": Radar,
    "EnergyGenerator": EnergyGenerator,
}
