class generalMenuObject(object):
    def __init__(self, parent, raw):
        self.parent = parent
        self.raw = raw
        self.children = []
        
    def __iter__(self):
        if type(self.children) is dict:
            return iter(self.children.values())
        else:
            return iter(self.children)

class Reservation(generalMenuObject):
    def __init__(self, parent_meal, obj):
        super().__init__(parent_meal, obj)
        self.food_id = obj["FoodId"]
        self.self_id = obj["SelfId"]

class SelfService(generalMenuObject):
    def __init__(self, parent_food, obj):
        super().__init__(parent_food, obj)
        
        self.id = obj["SelfId"]
        self.name = obj["SelfName"]
        self.price = obj["Price"]
        self.reservation = False

        if self.parent.reservation:
            self.reservation = self.parent.parent.reservation.self_id == self.id
    
    def __str__(self):
        emoji = {True: "🟢", False: "🔵"}
        return f"    {emoji[self.reservation]} {self.name} : {self.price}"
