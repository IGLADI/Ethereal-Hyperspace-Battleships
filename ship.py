from location import Location
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

_MODULE_MAPS = {
    "Module": Module,
    "SolarPanel": SolarPanel,
    "TravelModule": TravelModule,
    "MiningModule": MiningModule,
    "Canon": Canon,
    "Shield": Shield,
    "Fuel": Fuel,
    "Cargo": Cargo,
    "Radar": Radar,
    "EnergyGenerator": EnergyGenerator,
}

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
            module = _MODULE_MAPS.get(type)
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

    def change_energy(self, amount):
        self._energy += amount

    def remove_resource(self, resource_name, amount):
        for resource in self.modules["Cargo"]._capacity:
            if resource.name == resource_name:
                resource.amount -= amount
                break

    def add_resource(self, resource_name, amount):
        for resource in self.modules["Cargo"]._capacity:
            if resource.name == resource_name:
                resource.amount += amount
                break

    @classmethod
    def store(cls, discord_id):
        """Registers a new ship with default modules."""
        global _db
        _db.store_ship(discord_id)

        ship_id = _db.player_ship_id(discord_id)
        for module in DEFAULT_MODULES:
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
                # TODO Use database to fix this (way easier than using data.py file)!
                    locations.append()
        return locations
