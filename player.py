from ship import Ship
from utils import get_betted_amount
from threading import Thread
import time

# TODO when implementing the db, on load of the players call init with values (and put actual values as default values)
class Player:
    def __init__(self, id):
        self.id = id
        self._money = 1000
        self._ship = Ship()
        self._energy_thread = Thread(target=self.update_energy)
        self._energy_thread.daemon = True
        self._energy_thread.start()

    @property
    def money(self):
        betted_amount = get_betted_amount(self.id)
        return self._money - betted_amount

    @property
    def ship(self):
        return self._ship

    @money.setter
    def money(self, amount):
        if amount >= 0:
            self._money = amount
        else:
            self._money = 0

    # TODO make a secondary module like solar panels (slow but doesn't consume uranium=>players don't get stuck)
    def update_energy(self):
        while True:
            # always use 1 uranium for now, will probably add a different rendement per level later on
            for resource in self.ship.modules[5]._capacity:
                if resource.name == "Uranium":
                    uranium_amount = resource.amount
                    break
            if self.ship.energy < 100 and uranium_amount >= 1:
                self.ship.add_energy(1)
                self._ship.remove_resource("Uranium", 1)
            time.sleep(60)
