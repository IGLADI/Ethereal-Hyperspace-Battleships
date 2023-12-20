from database import Database
_db = Database()


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
        return _db.location_from_coordinates(self.x, self.y)
    
    def distance_to(self, location):
        '''Returns the distance between two locations'''
        return ((self.x - location.x) ** 2 + (self.y - location.y) ** 2) ** 0.5