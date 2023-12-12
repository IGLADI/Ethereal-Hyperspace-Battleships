from ship import Ship

class Player:
    def __init__(self, id):
        self.id = id
        self._money = 1000
        self._ship = Ship()

    @property
    def money(self):
        return self._money

    @property
    def ship(self):
        return self._ship

    @money.setter
    def money(self, amount):
        if amount >= 0:
            self._money = amount
        else:
            self._money = 0