from random import randrange
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
    
    def get_image(self):
        '''Returns the image of the location'''
        image_info = _db.location_image(self.x, self.y)
        if image_info == []:
            int_image = randrange(0, 4)
            return f"assets/space/space{int_image}.jpg", "space"
        if image_info[0][0] == None:
            int_image = randrange(0, 9)
            image = f"assets/planet/planet{int_image}.jpg"
            _db.set_location_image(self.x, self.y, image)
            return image, image_info[0][1]
        if image_info:
            return image_info[0][0], image_info[0][1]
