from location import Location
from module import Travel_Module, Mining_Module, Canon, Shield, Fuel, Cargo, Radar, Energy_Generator


class Ship:
    def __init__(self):
        self._modules = []
        self._location = Location(0, 0)
        self._modules.append(Travel_Module())
        self._modules.append(Mining_Module())
        self._modules.append(Canon())
        self._modules.append(Shield())
        self._modules.append(Fuel())
        self._modules.append(Cargo())
        self._modules.append(Radar())
        self._modules.append(Energy_Generator())

    @property
    def modules(self):
        return self._modules

    @property
    def location(self):
        return self._location
