from utils import get_betted_amount


class Player:
    def __init__(self, id):
        self.id = id
        self._money = 1000

    @property
    def money(self):
        betted_amount = get_betted_amount(self.id)
        return self._money - betted_amount

    @money.setter
    def money(self, amount):
        if amount >= 0:
            self._money = amount
        else:
            self._money = 0
