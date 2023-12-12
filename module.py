# The comments show the properties of each module at each level. These can be changed as we need to balance the game.
class Module:
    def __init__(self, name, description, max_level, cost):
        self._name = name
        self._description = description
        self._level = 1
        self._max_level = max_level
        self._cost = cost
    
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
    
    def upgrade(self):
        self._level += 1

class Travel_Module(Module):
    def __init__(self):
        super().__init__("Travel Module", "Increases the distance the ship can travel.", 6, [{"resource": "money", "amount": 100}, {"resource": "copper", "amount": 300}])
        self._max_distance = 1000
    
    @property
    def max_distance(self):
        return self._max_distance

    # max_distance levels:  1000,   1500,   1900,   2200,     2400,     2500
    # money cost levels:    100,    300,    900,    2700,     8100,     24300
    # copper cost levels:   300,    600,    900,    1200,     1500,     1800
    def upgrade(self):
        if self._level == self._max_level:
            raise Exception("Module is already at max level.")
        super().upgrade()
        upgrade_amount = 500 - (100 * (self.level - 1))
        self._max_distance += upgrade_amount
        self._cost[0]["amount"] *= 3
        self._cost[1]["amount"] += 300

class Mining_Module(Module):
    def __init__(self):
        super().__init__("Mining Module", "Increases the amount of resources the ship can mine.", 5, [{"resource": "money", "amount": 100}, {"resource": "silver", "amount": 300}])
        self._mining_bonus = 100
    
    @property
    def mining_bonus(self):
        return self._mining_bonus
    
    # mining_bonus levels:  100,    101,    103,    105,    110
    # money cost levels:    100,    300,    900,    2700,   8100
    # silver cost levels:   300,    600,    900,    1200,   1500
    def upgrade(self):
        if self._level == self._max_level:
            raise Exception("Module is already at max level.")
        super().upgrade()
        if self.level == 2:
            self._mining_bonus += 1
        elif self.level == 3 or self.level == 4:
            self._mining_bonus += 2
        elif self.level == 5:
            self._mining_bonus += 5
        self._cost[0]["amount"] *= 3
        self._cost[1]["amount"] += 300

class Cargo(Module):
    def __init__(self):
        super().__init__("Cargo", "Increases the amount of cargo the ship can hold.", 6, [{"resource": "money", "amount": 100}, {"resource": "gold", "amount": 300}])
        self._max_capacity = 1000
        self._capacity = []
    
    @property
    def max_capacity(self):
        return self._max_capacity
    
    @property
    def capacity(self):
        return self._capacity
    
    # max_capacity levels:  1000,   1500,   1900,   2200,   2400,   2500
    # money cost levels:    100,    300,    900,    2700,   8100,   24300
    # gold cost levels:     300,    600,    900,    1200,   1500,   1800
    def upgrade(self):
        if self._level == self._max_level:
            raise Exception("Module is already at max level.")
        super().upgrade()
        upgrade_amount = 500 - (100 * (self.level - 1))
        self._max_capacity += upgrade_amount
        self._cost[0]["amount"] *= 3
        self._cost[1]["amount"] += 300
    
