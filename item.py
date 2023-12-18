from database import Database


_db = Database()


class Item:
    def __init__(self, item_id):
        global _db
        amount = _db.item_amount(item_id)
        name = _db.item_name(item_id)
        print("name:", name)
        print("amount:", amount)

        self._id = item_id
        self._name = name
        self._amount = amount
        self._max_amount = 100

    @property
    def id(self) -> int:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def amount(self) -> int:
        return self._amount

    @property
    def max_amount(self) -> int:
        return self._max_amount

    @amount.setter
    def amount(self, amount):
        if amount > self.max_amount:
            raise ValueError(f"Can not assign more than max_amount: {self.max_amount}")
        global _db
        self._amount = amount
        if amount == 0:
            _db.item_delete(self.id)
        else:
            _db.item_set_amount(self.id, amount)

    @max_amount.setter
    def max_amount(self, max_amount):
        self._max_amount = max_amount

    @classmethod
    def store(cls, name, item_type, amount, cargo_module_id):
        global _db
        _db.store_item(
            name=name,
            item_type=item_type,
            amount=amount,
            cargo_module_id=cargo_module_id,
        )

    def __str__(self):
        return f"{self.name}: {self.amount}/{self.max_amount}"


class Resource(Item):
    def __init__(self, item_id):
        super().__init__(item_id)

        resource_type = _db.item_type(item_id)
        self._type = resource_type

    @property
    def type(self) -> str:
        return self._type

    @classmethod
    def store(cls, name, amount, cargo_module_id):
        super().store(
            name=name,
            item_type="resource",
            amount=amount,
            cargo_module_id=cargo_module_id,
        )

    def contribute_resource(cls, building_id):
        global _db
        # TODO implementation
        # 1. check if enough of resource
        # 2. add in contributions
        # 3. remove from cargo
        _db.contribute_resource(item_id, building_id)
