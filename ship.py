from location import Location
from module import TravelModule, MiningModule, Canon, Shield, Fuel, Cargo, Radar, Energy_Generator

class Ship:
    def __init__(self):
        self._modules = []
        self._location = Location(0, 0)
        self._modules.append(TravelModule())
        self._modules.append(MiningModule())
        self._modules.append(Canon())
        self._modules.append(Shield())
        self._modules.append(Fuel())
        self._modules.append(Cargo())
        self._modules.append(Radar())
        self._modules.append(Energy_Generator())
        # TODO make this in apart battery module
        self._energy = 100
        self._energy_capacity = 100

    @property
    def energy_capacity(self):
        return self._energy_capacity

    @property
    def energy(self):
        return self._energy

    @property
    def modules(self):
        return self._modules

    @property
    def location(self):
        return self._location

    def add_energy(self, amount):
        self._energy += amount

    def remove_energy(self, amount):
        self._energy -= amount

    def remove_resource(self, resource_name, amount):
        for resource in self.modules[5]._capacity:
            if resource.name == resource_name:
                resource.amount -= amount
                break

    def add_resource(self, resource_name, amount):
        for resource in self.modules[5]._capacity:
            if resource.name == resource_name:
                resource.amount += amount
                break
