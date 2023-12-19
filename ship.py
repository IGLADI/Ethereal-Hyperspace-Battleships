from database import Database

from module import (
    Module,
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

_db = Database()

import time
import threading


class Ship:
    def __init__(self, ship_id):
        global _db
        module_ids = _db.ship_module_ids(ship_id)

        modules = {}
        for module_id in module_ids:
            type = _db.module_type(module_id)
            module = DEFAULT_MODULES.get(type)
            modules[type] = module(module_id)

        self.id = ship_id
        self._modules = modules
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

    @energy.setter
    def energy(self, energy):
        self._energy = energy

    @classmethod
    def store(cls, discord_id):
        """Stores a new ship with default modules."""
        global _db
        _db.store_ship(discord_id)

        ship_id = _db.player_ship_id(discord_id)
        for module in DEFAULT_MODULES.values():
            module.store(ship_id)
            
    def location(self):
        return self._location
    
    @property
    def is_traveling(self):
        return self._is_traveling
    
    def travel(self, x_coordinate, y_coordinate):
        '''Travels to the given coordinates'''
        old_location = self._location
        new_location = Location(x_coordinate, y_coordinate)
        distance = int(old_location.distance_to(new_location))
        if distance > self._modules[0].max_distance:
            raise Exception("You can't travel that far! You need to upgrade your travel module.")
        
        def travel_thread():
            self._is_traveling = True
            while self._location.x != new_location.x or self._location.y != new_location.y:
                if self._location.x < new_location.x:
                    self._location.x += 1
                elif self._location.x > new_location.x:
                    self._location.x -= 1
                if self._location.y < new_location.y:
                    self._location.y += 1
                elif self._location.y > new_location.y:
                    self._location.y -= 1
                time.sleep(1)
            self._is_traveling = False
        
        travel_thread_instance = threading.Thread(target=travel_thread)
        travel_thread_instance.start()
        return distance
    
    def scan(self):
        '''Returns a list of locations in a grid around the ship, depending on the radar module level'''
        scan_range = self._modules[6].radar_range//2
        location = self._location
        locations = []
        for i in range(location.get_x() - scan_range, location.get_x() + scan_range):
            for j in range(location.get_y() - scan_range, location.get_y() + scan_range):
                is_location = _db.location_from_coos(i, j)
                if is_location != None:
                    locations.append(is_location)
        return locations
