from resources import Resource

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

    def __str__(self):
        cost_str = "".join(f"\n   - {cost['resource']}: {cost['amount']}" for cost in self._cost)
        if self._level == self._max_level:
            return f" - **Name: {self._name}**\n - Description: {self._description}\n - Level: {self._level}/{self._max_level}\n - Upgrade Cost: MAX LEVEL\n"
        return f" - **Name: {self._name}**\n - Description: {self._description}\n - Level: {self._level}/{self._max_level}\n - Upgrade Cost: {cost_str}\n"

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
        upgrade_amount = 500 - (100 * (self.level - 2))
        self._max_distance += upgrade_amount
        self._cost[0]["amount"] *= 3
        self._cost[1]["amount"] += 300

    def __str__(self):
        return f"{super().__str__()} - Max Distance: {self._max_distance} lightyears\n"

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

    def __str__(self):
        return f"{super().__str__()} - Mining Bonus: {self._mining_bonus}%\n"

class Cargo(Module):
    def __init__(self):
        super().__init__("Cargo", "Increases the amount of cargo the ship can hold.", 6, [{"resource": "money", "amount": 100}, {"resource": "gold", "amount": 300}])
        self._max_capacity = 1000
        self._capacity = []
        self._capacity.append(Resource("copper", 0))
        self._capacity.append(Resource("silver", 0))
        self._capacity.append(Resource("gold", 0))
    
    @property
    def max_capacity(self):
        return self._max_capacity
    
    @property
    def capacity(self):
        return self._capacity
    
    def add_cargo(self, resource, amount):
        max_amount = self._max_capacity - sum(cargo.get_amount() for cargo in self._capacity)
        if amount > max_amount:
            amount = max_amount
        for cargo in self._capacity:
            if cargo.get_name() == resource:
                cargo.amount += amount
                return amount
    
    # max_capacity levels:  1000,   1500,   1900,   2200,   2400,   2500
    # money cost levels:    100,    300,    900,    2700,   8100,   24300
    # gold cost levels:     300,    600,    900,    1200,   1500,   1800
    def upgrade(self):
        if self._level == self._max_level:
            raise Exception("Module is already at max level.")
        super().upgrade()
        upgrade_amount = 500 - (100 * (self.level - 2))
        self._max_capacity += upgrade_amount
        self._cost[0]["amount"] *= 3
        self._cost[1]["amount"] += 300

    def __str__(self):
        capacity_str = "".join(f"\n   - {str(cargo)}" for cargo in self._capacity)
        return f"{super().__str__()} - Capacity: {capacity_str} \n - Max Capacity: {self._max_capacity} tons\n"
    
class Canon(Module):
    def __init__(self):
        super().__init__("Canon", "Increases the ship's attack damage.", 5, [{"resource": "money", "amount": 200}, {"resource": "copper", "amount": 150}, {"resource": "silver", "amount": 150}, {"resource": "gold", "amount": 150}])
        self._strength = 100
    
    @property
    def strength(self):
        return self._strength
    
    # strength levels:      100,    110,    130,    145,    150
    # money cost levels:    200,    600,    1200,   3600,   10800
    # copper cost levels:   150,    300,    450,    600,    750
    # silver cost levels:   150,    300,    450,    600,    750
    # gold cost levels:     150,    300,    450,    600,    750
    def upgrade(self):
        if self._level == self._max_level:
            raise Exception("Module is already at max level.")
        super().upgrade()
        if self.level == 2:
            self._strength += 10
        elif self.level == 3:
            self._strength += 20
        elif self.level == 4:
            self._strength += 15
        elif self.level == 5:
            self._strength += 5
        self._cost[0]["amount"] *= 3
        self._cost[1]["amount"] += 150
        self._cost[2]["amount"] += 150
        self._cost[3]["amount"] += 150

    def __str__(self):
        return f"{super().__str__()} - Strength: {self._strength} firepower\n"

class Shield(Module):
    def __init__(self):
        super().__init__("Shield", "Increases the ship's defense.", 5, [{"resource": "money", "amount": 200}, {"resource": "copper", "amount": 150}, {"resource": "silver", "amount": 150}, {"resource": "gold", "amount": 150}])
        self._defense = 100
    
    @property
    def defense(self):
        return self._defense
    
    # defense levels:       100,    110,    130,    145,    150
    # money cost levels:    200,    600,    1200,   3600,   10800
    # copper cost levels:   150,    300,    450,    600,    750
    # silver cost levels:   150,    300,    450,    600,    750
    # gold cost levels:     150,    300,    450,    600,    750
    def upgrade(self):
        if self._level == self._max_level:
            raise Exception("Module is already at max level.")
        super().upgrade()
        if self.level == 2:
            self._defense += 10
        elif self.level == 3:
            self._defense += 20
        elif self.level == 4:
            self._defense += 15
        elif self.level == 5:
            self._defense += 5
        self._cost[0]["amount"] *= 3
        self._cost[1]["amount"] += 150
        self._cost[2]["amount"] += 150
        self._cost[3]["amount"] += 150
    
    def __str__(self):
        return f"{super().__str__()} - Defense: {self._defense} armor\n"

class Fuel(Module):
    def __init__(self):
        super().__init__("Fuel", "Increases the ship's fuel capacity.", 6, [{"resource": "money", "amount": 200}, {"resource": "copper", "amount": 150}, {"resource": "silver", "amount": 150}, {"resource": "gold", "amount": 150}])
        self._max_fuel = 1000
        self._fuel = 1000
    
    @property
    def max_fuel(self):
        return self._max_fuel
    
    @property
    def fuel(self):
        return self._fuel
    
    # max_fuel levels:      1000,   1500,   1900,   2200,   2400,   2500
    # money cost levels:    200,    600,    1200,   3600,   10800,  32400
    # copper cost levels:   150,    300,    450,    600,    750,    750
    # silver cost levels:   150,    300,    450,    600,    750,    750
    # gold cost levels:     150,    300,    450,    600,    750,    750
    def upgrade(self):
        if self._level == self._max_level:
            raise Exception("Module is already at max level.")
        super().upgrade()
        upgrade_amount = 500 - (100 * (self.level - 2))
        self._max_fuel += upgrade_amount
        self._fuel += upgrade_amount
        self._cost[0]["amount"] *= 3
        if self.level < 6:
            self._cost[1]["amount"] += 150
            self._cost[2]["amount"] += 150
            self._cost[3]["amount"] += 150

    def __str__(self):
        return f"{super().__str__()} - Current Fuel: {self._fuel} liters - Max Fuel: {self._max_fuel} liters\n"

class Radar(Module):
    def __init__(self):
        super().__init__("Radar", "Increases the ship's radar range.", 7, [{"resource": "money", "amount": 500}, {"resource": "copper", "amount": 50}, {"resource": "silver", "amount": 50}, {"resource": "gold", "amount": 50}])
        self._radar_range = 1000
    
    @property
    def radar_range(self):
        return self._radar_range
    
    # radar_range levels:   50,     60,     70,     80,     90,     95,     100
    # money cost levels:    500,    1000,   2000,   4000,   8000,   16000,  32000
    # copper cost levels:   50,     150,    250,    350,    450,    550,    650
    # silver cost levels:   50,     150,    250,    350,    450,    550,    650
    # gold cost levels:     50,     200,    350,    500,    650,    800,    950
    def upgrade(self):
        if self._level == self._max_level:
            raise Exception("Module is already at max level.")
        super().upgrade()
        if self.level < 6:
            self._radar_range += 10
        else:
            self._radar_range += 5
        self._cost[0]["amount"] *= 2
        self._cost[1]["amount"] += 100
        self._cost[2]["amount"] += 100
        self._cost[3]["amount"] += 150

    def __str__(self):
        return f"{super().__str__()} - Radar Range: {self._radar_range} lightyears\n"

# generation = amount / minute
class Energy_Generator(Module):
    def __init__(self):
        super().__init__("Energy Generator", "Increases the ship's energy generation and maximum energy capacity.", 7, [{"resource": "money", "amount": 1000}, {"resource": "copper", "amount": 200}, {"resource": "silver", "amount": 200}, {"resource": "gold", "amount": 500}])
        self._max_energy = 100
        self._generation = 1

    @property
    def max_energy(self):
        return self._max_energy
    
    @property
    def generation(self):
        return self._generation
    
    # max_energy levels:    100,    150,    200,    300,    450,    600,    750
    # generation levels:    1,      2,      3,      5,      7,      10,     10
    # money cost levels:    1000,   2000,   4000,   8000,   16000,  32000,  64000
    # copper cost levels:   200,    350,    500,    650,    800,    950,    1000
    # silver cost levels:   200,    350,    500,    650,    800,    950,    1000
    # gold cost levels:     500,    500,    500,    500,    500,    500,    500
    def upgrade(self):
        if self._level == self._max_level:
            raise Exception("Module is already at max level.")
        super().upgrade()
        if self.level == 2 or self.level == 3:
            self._max_energy += 50
            self._generation += 1
        elif self.level == 4:
            self._max_energy += 100
            self._generation += 2
        elif self.level == 5:
            self._max_energy += 150
            self._generation += 2
        else:
            self._max_energy += 150
            if self.level < 7:
                self._generation += 3
        self._cost[0]["amount"] *= 2
        if self.level < 7:
            self._cost[1]["amount"] += 150
            self._cost[2]["amount"] += 150
        else:
            self._cost[1]["amount"] += 50
            self._cost[2]["amount"] += 50

    def __str__(self):
        return f"{super().__str__()} - Max Energy: {self._max_energy} - Generation: {self._generation} per minute\n"