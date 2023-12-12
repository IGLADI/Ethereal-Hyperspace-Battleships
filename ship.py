from location import Location
from module import Travel_Module
from module import Mining_Module
from module import Cargo

class Ship:

    def __init__(self):
        self._modules = []
        self._location = Location(0, 0)
        self._modules.add(Travel_Module())
        self._modules.add(Mining_Module())
        self._modules.add(Cargo())

    @property
    def modules(self):
        return self._modules

    @property
    def location(self):
        return self._location