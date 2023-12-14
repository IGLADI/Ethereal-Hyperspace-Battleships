from location import Location
from module import TravelModule, MiningModule, Canon, Shield, Fuel, Cargo, Radar, EnergyGenerator


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
        self._modules.append(EnergyGenerator())

    @property
    def modules(self):
        return self._modules

    @property
    def location(self):
        return self._location
