from database import Database

_db = Database()


class Coordinate:
    def __init__(self, x, y):
        "Represents a coordinate."
        self._x = x
        self._y = y

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, x):
        self._x = x

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, y):
        self._y = y

    def is_location(self) -> bool:
        """Check if there is a location at this position."""
        global _db
        return True if _db.location_init(self.x, self.y) is not None else False

    def distance_to(self, pos: "Coordinate") -> float:
        """Returns the distance between two locations"""
        # Euclidean distance
        return ((self.x - pos.x) ** 2 + (self.y - pos.y) ** 2) ** 0.5


class Location:
    def __init__(self, x_pos, y_pos):
        global _db
        name, image_path = _db.location_init(x_pos=x_pos, y_pos=y_pos)

        self._x = x_pos
        self._y = y_pos

        self._image_path = image_path
        self._name = name

    @classmethod
    def fromcoordinate(cls, coordinate: Coordinate):
        return cls(coordinate.x, coordinate.y)

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def image_path(self):
        return self._image_path

    @property
    def name(self):
        return self._name

    def is_planet(self):
        """Returns the planet id if the location is a planet."""
        raise NotImplementedError

    def __str__(self):
        return f"{self.name}: ({self.x}, {self.y}) [{self.image_path}]"
