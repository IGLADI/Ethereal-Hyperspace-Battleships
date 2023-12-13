# Temporary for ship creation purposes
class Resource:
    def __init__(self, name, amount, max_amount):
        self.name = name
        self.amount = amount
        self._max_amount = max_amount

    @property
    def get_name(self):
        return self.name

    @property
    def get_amount(self):
        return self.amount
    
    @property
    def max_amount(self):
        return self._max_amount
    
    @max_amount.setter
    def max_amount(self, amount):
        self._max_amount = amount
    
    def __str__(self):
        return f"{self.name}: {self.amount}"