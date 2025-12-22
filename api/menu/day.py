from .general import generalMenuObject
from .meal import Meal

class Day(generalMenuObject):
    def __init__(self, parent_menu, obj):
        super().__init__(parent_menu, obj)
        
        self.day_id = obj["DayId"]
        self.day_date = obj["DayDate"]
        self.day_title = obj["DayTitle"]
        self.day_state = obj["DayState"]
        self.day_state_title = obj["DayStateTitle"]
        self.children = {}
        for i, meal in enumerate(obj["Meals"]):
            if x := Meal(self, meal):
                self.children[i+1] = x
    
    def getPrice(self, skip_reserved, filters):
        return sum(x.getPrice(skip_reserved, filters=filters) for x in self)
    
    def __str__(self, filters=[]):
        return f"🗓 {self.day_title}، {self.day_date}\n{'\n'.join(x.__str__(filters=filters) for x in self)}"
    
    def __bool__(self):
        return bool(self.children)


    def apply_filter(self, filters):
        new_meal_list = []
        for meal in self:
            if new_meal := meal.apply_filter(filters):
                new_meal_list.append(new_meal)
        if new_meal_list:
            self.children = new_meal_list
            return self
        else:
            return None
