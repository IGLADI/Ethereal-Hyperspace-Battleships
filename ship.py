from location import Location
from module import (
    SolarPanel,
    TravelModule,
    MiningModule,
    Canon,
    Shield,
    Fuel,
    Cargo,
    Radar,
    EnergyGenerator,
    DEFAULT_MODULES,
)


class Ship:
    def __init__(self):
        self._modules = {module.__name__: module() for module in DEFAULT_MODULES}
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

    def change_energy(self, amount):
        self._energy += amount

    def remove_resource(self, resource_name, amount):
        for resource in self.modules["Cargo"]._capacity:
            if resource.name == resource_name:
                resource.amount -= amount
                break

    def add_resource(self, resource_name, amount):
        for resource in self.modules["Cargo"]._capacity:
            if resource.name == resource_name:
                resource.amount += amount
                break
