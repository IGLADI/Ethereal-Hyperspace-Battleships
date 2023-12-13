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
    
    def upgrade(self, cargo_player):
        if self._level == self._max_level:
            raise Exception("Module is already at max level.")
        if not self.has_enough_resources(cargo_player):
            raise Exception("Not enough resources to upgrade.")
        self._level += 1
        self.consume_resources(cargo_player)  # You need to implement this method to consume the required resources.

    def has_enough_resources(self, cargo_player):
        for cost in self._cost:
            resource_name = cost["resource"]
            required_amount = cost["amount"]

            if cargo_player.get_resource_amount(resource_name) < required_amount:
                return False

        return True

    def consume_resources(self, cargo_player):
        for cost in self._cost:
            resource_name = cost["resource"]
            required_amount = cost["amount"]

            cargo_player.consume_resource(resource_name, required_amount)

    def __str__(self):
        cost_str = "".join(f"\n   - {cost['resource']}: {cost['amount']}" for cost in self._cost)
        if self._level == self._max_level:
            return f" - **Name: {self._name}**\n - Description: {self._description}\n - Level: {self._level}/{self._max_level}\n - Upgrade Cost: MAX LEVEL\n"
        return f" - **Name: {self._name}**\n - Description: {self._description}\n - Level: {self._level}/{self._max_level}\n - Upgrade Cost: {cost_str}\n"

class Travel_Module(Module):
    def __init__(self):
        super().__init__("Travel Module", "Increases the distance the ship can travel.", 6, [{"resource": "Money", "amount": 0}, {"resource": "Copper", "amount": 200}, {"resource": "Silver", "amount": 0}, {"resource": "Gold", "amount": 0}])
        self._max_distance = 1000
    
    @property
    def max_distance(self):
        return self._max_distance

    # max_distance levels:  1000,   1500,   1900,   2200,     2400,     2500
    # money cost levels:    100,    300,    900,    2700,     8100,     24300
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

class Mining_Module(Module):
    def __init__(self):
        super().__init__("Mining Module", "Increases the amount of resources the ship can mine.", 5, [{"resource": "Money", "amount": 0}, {"resource": "Copper", "amount": 150}, {"resource": "Silver", "amount": 150}, {"resource": "Gold", "amount": 150}])
        self._mining_bonus = 100
    
    @property
    def mining_bonus(self):
        return self._mining_bonus
    
    # mining_bonus levels:  100,    101,    103,    105,      110
    # money cost levels:    100,    300,    900,    2700,     8100
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
    def __init__(self):
        super().__init__("Cargo", "Increases the amount of cargo the ship can hold.", 6, [{"resource": "Money", "amount": 0}, {"resource": "Copper", "amount": 150}, {"resource": "Silver", "amount": 150}, {"resource": "Gold", "amount": 150}])
        self._max_capacity = 300
        self._inventory = []
        self._inventory.append(Resource("Copper", 0, self._max_capacity))
        self._inventory.append(Resource("Silver", 0, self._max_capacity))
        self._inventory.append(Resource("Gold", 0, self._max_capacity))
        self._inventory.append(Resource("Uranium", 0, self._max_capacity))
        self._inventory.append(Resource("Black Matter", 0, self._max_capacity))
    
    #individual per resource
    @property
    def max_capacity(self):
        return self._max_capacity
    
    @property
    def inventory(self):
        return self._inventory
    
    def get_resource_amount(self, resource_name):
        for resource in self._inventory:
            if resource.name.lower() == resource_name.lower():
                return resource.amount
        return 0
    
    def consume_resource(self, resource_name, amount):
        for resource in self._inventory:
            if resource.name.lower() == resource_name.lower():
                resource.amount -= amount
                return
    
    def add_cargo(self, resource, amount):
        # Dictionary that maps resource names to indices in the inventory list
        resource_indices = {
            "copper": 0,
            "silver": 1,
            "gold": 2,
            "uranium": 3,
            "black matter": 4
        }

        resource_lower = resource.lower()
        if resource_lower in resource_indices:
            index = resource_indices[resource_lower]
            max_amount = self._max_capacity - self._inventory[index].amount
        else:
            max_amount = 0
            
        if amount > max_amount:
            amount = max_amount

        for cargo in self._inventory:
            if cargo.name.lower() == resource_lower:
                cargo.amount += amount

        return amount
    
    # max_capacity levels:  300,    400,    500,    600,      800,      1000
    # money cost levels:    100,    300,    900,    2700,     8100,     24300
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

    def __str__(self):
        inventory_str = "".join(f"\n   - {str(cargo)}" for cargo in self._inventory)
        return f"{super().__str__()} - Inventory: {inventory_str} \n - Max Capacity: {self._max_capacity} tons\n"
    
class Canon(Module):
    def __init__(self):
        super().__init__("Canon", "Increases the ship's attack damage.", 5, [{"resource": "Money", "amount": 0}, {"resource": "Copper", "amount": 150}, {"resource": "Silver", "amount": 150}, {"resource": "Gold", "amount": 150}])
        self._strength = 100
    
    @property
    def strength(self):
        return self._strength
    
    # strength levels:      100,    110,    130,    145,    150
    # money cost levels:    200,    600,    1200,   3600,   10800
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
    def __init__(self):
        super().__init__("Shield", "Increases the ship's defense.", 5, [{"resource": "Money", "amount": 0}, {"resource": "Copper", "amount": 150}, {"resource": "Silver", "amount": 150}, {"resource": "Gold", "amount": 150}])
        self._defense = 100
    
    @property
    def defense(self):
        return self._defense
    
    # defense levels:       100,    110,    130,    145,    150
    # money cost levels:    200,    600,    1200,   3600,   10800
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
    def __init__(self):
        super().__init__("Fuel", "Holds the ship's fuel.", 1, [{"resource": "Money", "amount": 0}, {"resource": "Copper", "amount": 0}, {"resource": "Silver", "amount": 0}, {"resource": "Gold", "amount": 0}])
        self._fuel = 100
    
    @property
    def fuel(self):
        return self._fuel
    
    def upgrade(self, cargo_player):
        super().upgrade(cargo_player)

    def __str__(self):
        return f"{super().__str__()} - Current Fuel: {self._fuel}%\n"

class Radar(Module):
    def __init__(self):
        super().__init__("Radar", "Increases the ship's radar range.", 7, [{"resource": "Money", "amount": 0}, {"resource": "Copper", "amount": 50}, {"resource": "Silver", "amount": 50}, {"resource": "Gold", "amount": 50}])
        self._radar_range = 50
    
    @property
    def radar_range(self):
        return self._radar_range
    
    # radar_range levels:   50,     60,     70,     80,     90,     95,     100
    # money cost levels:    500,    1000,   2000,   4000,   8000,   16000,  32000
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
class Energy_Generator(Module):
    def __init__(self):
        super().__init__("Energy Generator", "Increases the ship's energy generation.", 7, [{"resource": "Money", "amount": 0}, {"resource": "Copper", "amount": 50}, {"resource": "Silver", "amount": 50}, {"resource": "Gold", "amount": 50}])
        self._generation = 1
    
    @property
    def generation(self):
        return self._generation
    
    # generation levels:    1,      2,      3,      5,      7,      10,     13
    # money cost levels:    0,      0,      0,      0,      0,      0,      0
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