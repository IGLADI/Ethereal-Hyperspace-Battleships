from location import Location
from module import TravelModule, MiningModule, Canon, Shield, Fuel, Cargo, Radar, EnergyGenerator

import time
import threading


class Ship:
    def __init__(self):
        self._modules = []
        self._location = Location(0, 0)
        self._is_traveling = False
        self._modules.append(TravelModule())
        self._modules.append(MiningModule())
        self._modules.append(Canon())
        self._modules.append(Shield())
        self._modules.append(Fuel())
        self._modules.append(Cargo())
        self._modules.append(Radar())
        self._modules.append(EnergyGenerator())

    @property
    def modules(self):
        return self._modules

    @property
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
            while self._location != new_location:
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
