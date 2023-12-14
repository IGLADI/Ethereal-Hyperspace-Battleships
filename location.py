from data import planets

class Location:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y
    
    def __str__(self):
        return f"({self.x}, {self.y})"

    def is_planet(self):
        '''Returns the planet name if the location is a planet, otherwise returns space'''
        for planet in planets.values():
            if self.x == planet.location.x and self.y == planet.location.y:
                return f"at {planet.name}"
        return "floating in space"