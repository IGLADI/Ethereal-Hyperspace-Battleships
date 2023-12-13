from location import Location

class Planet:
    def __init__(self, name, x, y):
        self.name = name
        self.location = Location(x, y)

    @property
    def name(self):
        return self._name

    @property
    def location(self):
        return self._location

    @name.setter
    def name(self, name):
        self._name = name

    @location.setter
    def location(self, location):
        self._location = location