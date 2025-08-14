class mealFilter(object):
    meal_name = {1:"صبحانه", 2: "ناهار", 3: "شام", 4: "افطار", 5: "سحری"}
    def __init__(self, meal, invert=False):
        if not ((type(meal) is int) and (1 <= meal <= 5)):
            raise
        self.meal = meal
        self.name = self.meal_name[meal]
        self.invert = invert

    def as_dict(self):
        return {'type': "meal", "meal": self.meal, "invert": self.invert}
    
    def __str__(self):
        return f"filter type: meal. meal: {self.name}, exclude: {self.invert}"

    def check(self, food):
        return self.invert ^ (food.parent.meal_id_day == self.meal)

class dayFilter(object):
    day_name = {0:"شنبه", 1: "یکشنبه", 2: "دوشنبه", 3: "سه شنبه", 4: "چهارشنبه", 5:"پنجشنبه", 6: "جمعه"}
    def __init__(self, day, invert=False):
        if not ((type(day) is int) and (1 <= day <= 7)):
            raise
        self.day = day
        self.name = self.day_name[day]
        self.invert = invert

    def as_dict(self):
        return {'type': "day", "day": self.day, "invert": self.invert}
    
    def __str__(self):
        return f"filter type: day. day: {self.name}, exclude: {self.invert}"

    def check(self, food):
        return self.invert ^ (food.parent.parent.day_id == self.day)

class foodFilter(object):
    def __init__(self, food, invert=False):
        if not (type(food) is str):
            raise
        self.food_name = food
        self.invert = invert

    def as_dict(self):
        return {'type': "food", "food": self.food_name, "invert": self.invert}
    
    def __str__(self):
        return f"filter type: food. food: {self.food_name}, exclude: {self.invert}"

    def check(self, food):
        return self.invert ^ (self.food_name in food.name)