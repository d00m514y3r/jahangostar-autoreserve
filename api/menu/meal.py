from .food import Food
from .general import generalMenuObject, Reservation


class Meal(generalMenuObject):
    def __init__(self, parent_day, obj):
        super().__init__(parent_day, obj)

        self.meal_id_week = obj["Id"]
        self.meal_id_day = obj["MealId"]
        self.day_name = obj["DayName"]
        self.meal_state = obj["MealState"]
        self.meal_state_title = obj["MealStateTitle"]
        self.meal_name = obj["MealName"]
        self.date = obj["Date"]
        self.reservation = None
        if obj["LastReserved"]:
            self.reservation = Reservation(self, obj["LastReserved"][0])

        self.children = {x["FoodId"]:Food(self, x) for x in obj["FoodMenu"]}
        self.food_count = len(self.children)
        
    def getPrice(self, skip_reserved, filters):
        if self.food_count:
            if skip_reserved and self.reservation:
                return 0
            return max(food.getPrice(filters=filters) for food in self)
        return 0

    def __str__(self, filters=[]):
        self_filters = [f for f in filters if f.type == "self"]
        return f"⏰ {self.meal_name}\n{'\n'.join(
            x.__str__(filters=self_filters) for x in self)}"
    
    def apply_filter(self, filters):
        new_food_menu = {}
        for food in self:
            for f in filters:
                if not f.check(food):
                    break
            else:
                new_food_menu[food.id] = food
        if new_food_menu:
            self.children = new_food_menu
            self.food_count = len(new_food_menu)
            return self
        else:
            return None
