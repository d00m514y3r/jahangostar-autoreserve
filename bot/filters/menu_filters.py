
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