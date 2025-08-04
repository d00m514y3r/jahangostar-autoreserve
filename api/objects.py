import logging

logger = logging.getLogger(__name__)

class Food(object):
    def __init__(self, parentMeal, http_client, obj):
        self.http_client = http_client
        self.parentMeal = parentMeal
        self.raw = obj
        self.id = obj["FoodId"]
        self.name = obj["FoodName"]
        self.price = obj["SelfMenu"][0]["Price"]
        self.self_name = obj["SelfMenu"][0]["SelfName"]
        self.self_id = obj["SelfMenu"][0]["SelfId"]
        self.self_count = len(obj["SelfMenu"])
        self.food_state = obj["FoodState"]
        if len(obj["SelfMenu"]) > 1:
            logger.warn(f"food {self.id} has more than one self service choice. using the first one...")
    
    def __str__(self):
        return f"{self.name}:{self.price}"
    
    def is_reserved(self):
        return self.parentMeal.is_reserved
    
    def change_reservation(self, count):
        if self.parentMeal.meal_state != 0 or self.food_state != 2:
            logger.error(f"failed to change reservation status of {self} due to inactive meal" )
            return {"ok": False, "result": "meal not active"}
        
        payload = {
            "Date":self.parentMeal.date,
            "MealId":self.parentMeal.meal_id_day,
            "FoodId":self.id,
            "SelfId":self.self_id,
            "PriceType":1,
            "Provider":1,
            "OP":1,
            "Counts": count
            }
        
        res = self.http_client.apiPost("Reservation", json=[payload])
        msg = res.json()[0]["StateMessage"]
        if "موفقیت" in msg:
            logger.info(f"{self} reservation changed status to {count}")
        elif "موجودی" in msg:
            logger.error(f"insufficient balance for reservation of {self}")
        else:
            logger.error(f"failed to change reservation for {self} / {msg}")
        return {"ok": False, "result": res}

    def reserve(self):
        if self.is_reserved():
            logger.error(f"attempted to reserve {self} which is already reserved")
            return None
        result = self.change_reservation(1)
        if result["ok"]:
            self.parentMeal.is_reserved = True
        return result["result"]
    
    def unreserve(self):
        if not self.is_reserved():
            logger.error(f"attempted to unreserve {self.id} which is not reserved")
            return False
        
        result = self.change_reservation(0)
        if result["ok"]:
            self.parentMeal.is_reserved = False
        return result["result"]

        

class Meal(object):
    def __init__(self, parentDay, http_client, obj):
        self.parentDay = parentDay
        self.http_client = http_client
        self.raw = obj
        self.meal_id_week = obj["Id"]
        self.meal_id_day = obj["MealId"]
        self.day_name = obj["DayName"]
        self.meal_state = obj["MealState"]
        self.meal_state_title = obj["MealStateTitle"]
        self.date = obj["Date"]
        self.is_reserved = bool(obj["LastReserved"])
        self.FoodMenu = [Food(self, http_client, food) for food in obj["FoodMenu"]]
        self.food_count = len(self.FoodMenu)
        if self.food_count > 1:
            logger.warn(f"food {self.id} has more than one self service choice")

    
    def getTotalPrice(self):
        return sum([x.price for x in self.FoodMenu])
    
    def getRemainingPrice(self):
        if self.is_reserved or self.meal_state != 0:
            return 0
        else:
            price = sum([x.price if x.food_state == 2 else 0 for x in self.FoodMenu])
            return price

    def __str__(self):
        return f"{self.date} - {self.meal_id_day} - {self.is_reserved}"
    
    def is_reserved(self):
        return self.is_reserved
    
class Day(object):
    def __init__(self, parentMenu, http_client, obj):
        self.parentMenu = parentMenu
        self.http_client = http_client
        self.raw = obj
        self.DayId = obj["DayId"]
        self.DayDate = obj["DayDate"]
        self.DayTitle = obj["DayTitle"]
        self.DayState = obj["DayState"]
        self.DayStateTitle = obj["DayStateTitle"]
        self.Meals = [Meal(self, http_client, meal) for meal in obj["Meals"]]
    
    def getTotalPrice(self):
        return sum([x.getTotalPrice() for x in self.Meals])
    
    def getRemainingPrice(self):
        return sum([x.getRemainingPrice() for x in self.Meals])

class Menu(object):
    def __init__(self, http_client, date=""):
        self.date = date
        self.http_client = http_client
        self.raw = self.get_menu(date=date)
        self.Days = [Day(self, http_client, day) for day in self.raw]
        self.current_date = date if date else self.Days[0].DayDate
    
    def get_menu(self, date="", navigation=0):
        obj = self.http_client.apiGet("Reservation", params={"lastdate": date, "navigation": navigation})
        return obj.json()
    
    def refresh_menu(self, date="", navigation=0):
        obj = self.get_menu(date=date, navigation=navigation)
        self.raw = obj
        self.Days = [Day(self, self.http_client, day) for day in self.raw]
    
    def getTotalPrice(self):
        return sum([x.getTotalPrice() for x in self.Days])
    
    def getRemainingPrice(self):
        return sum([x.getRemainingPrice() for x in self.Days])
    
    def __str__(self):
        res = []
        for day in self.Days:
            for meal in day.Meals:
                if not meal.FoodMenu:
                    continue
                food_text = []
                for food in meal.FoodMenu:
                    food_text.append(str(food))
                food_text = "/".join(food_text)
                x = f"{meal}: {food_text}"
                res.append(x)
        return "\n".join(res)