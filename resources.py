# Temporary for ship creation purposes
class Resource:
    def __init__(self, name, amount):
        self.name = name
        self.amount = amount

    def get_name(self):
        return self.name

    def get_amount(self):
        return self.amount
    
    def __str__(self):
        return f"{self.name}: {self.amount}"