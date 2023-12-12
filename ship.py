from location import Location
from module import Travel_Module
from module import Mining_Module
from module import Canon
from module import Shield
from module import Fuel
from module import Cargo
from module import Radar
from module import Energy_Generator

class Ship:

    def __init__(self):
        self._modules = set()
        self._location = Location(0, 0)
        self._modules.add(Travel_Module())
        self._modules.add(Mining_Module())
        self._modules.add(Canon())
        self._modules.add(Shield())
        self._modules.add(Fuel())
        self._modules.add(Cargo())
        self._modules.add(Radar())
        self._modules.add(Energy_Generator())

    @property
    def modules(self):
        return self._modules

    @property
    def location(self):
        return self._location