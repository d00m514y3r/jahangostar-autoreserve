import logging

logger = logging.getLogger(__name__)

class SelfService(object):
    def __init__(self, parentFood, obj):
        self.raw = obj
        self.id = obj["SelfId"]
        self.name = obj["SelfName"]
        self.price = obj["Price"]
    
    def __str__(self):
        return f"    🔺 {self.name} : {self.price}"

class Food(object):
    def __init__(self, parentMeal, http_client, obj):
        self.http_client = http_client
        self.parent_meal = parentMeal
        self.raw = obj
        self.id = obj["FoodId"]
        self.name = obj["FoodName"]
        self.self_menu = {x["SelfId"]: SelfService(self, x) for x in obj["SelfMenu"]}
        self.self_count = len(self.self_menu)
        self.food_state = obj["FoodState"]
        self.is_reserved = False
        if self.parent_meal.is_reserved:
            if self.id == self.parent_meal.raw["LastReserved"][0]["FoodId"]:
                self.is_reserved = True
        
    def __str__(self):
        if self.is_reserved:
            return f"  ✅ {self.name}\n{"\n".join(map(str, self.self_menu.values()))}"
        else:
            return f"  ❌ {self.name}\n{"\n".join(map(str, self.self_menu.values()))}"

    def getPrice(self):
        return max(x.price for x in self.self_menu.values())

    # TODO: delete function or move to Meal
    def is_reserved(self):
        return self.parent_meal.is_reserved
    
    # TODO: delete function or move to Meal
    def change_reservation(self, count):
        if self.parent_meal.meal_state != 0 or self.food_state != 2:
            logger.error(f"failed to change reservation status of {self} due to inactive meal" )
            return {"ok": False, "result": "meal not active"}
        
        payload = {
            "Date":self.parent_meal.date,
            "MealId":self.parent_meal.meal_id_day,
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
            return {"ok": True, "result": res}
        elif "موجودی" in msg:
            logger.error(f"insufficient balance for reservation of {self}")
        else:
            logger.error(f"failed to change reservation for {self} / {msg}")
        return {"ok": False, "result": res}

    def reserve(self):
        if self.is_reserved:
            logger.error(f"attempted to reserve {self} which is already reserved")
            return None
        result = self.change_reservation(1)
        if result["ok"]:
            self.parent_meal.is_reserved = True
        return result["result"]
    
    def unreserve(self):
        if not self.is_reserved:
            logger.error(f"attempted to unreserve {self.id} which is not reserved")
            return None
        result = self.change_reservation(0)
        if result["ok"]:
            self.parent_meal.is_reserved = False
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
        self.meal_name = obj["MealName"]
        self.date = obj["Date"]
        self.is_reserved = bool(obj["LastReserved"])

        self.food_menu = {x["FoodId"]:Food(self, http_client, x) for x in obj["FoodMenu"]}
        self.food_count = len(self.food_menu)
        
        self.service_selected = None
        self.food_selected = None

        if self.is_reserved:
            self.food_selected = self.food_menu[obj["LastReserved"][0]["FoodId"]]
            self.service_selected = self.food_selected.self_menu[obj["LastReserved"][0]["SelfId"]]

    def getPrice(self, check_reservation):
        if self.food_count:
            if check_reservation:
                if self.is_reserved:
                    return 0
                return max(x.getPrice() for x in self.food_menu.values())
            return max(x.getPrice() for x in self.food_menu.values())
        return 0        
    def __str__(self):
        return f"⏰ {self.meal_name}\n{"\n".join(map(str, self.food_menu.values()))}"            
    
class Day(object):
    def __init__(self, parentMenu, http_client, obj):
        self.parentMenu = parentMenu
        self.http_client = http_client
        self.raw = obj
        self.day_id = obj["DayId"]
        self.day_date = obj["DayDate"]
        self.day_title = obj["DayTitle"]
        self.day_state = obj["DayState"]
        self.day_state_title = obj["DayStateTitle"]
        self.meals = [Meal(self, http_client, meal) for meal in obj["Meals"]]
    
    def getPrice(self, check_reservation):
        return sum(x.getPrice(check_reservation) for x in self.meals)
    
    def __str__(self):
        return f"🗓 {self.day_title}، {self.day_date}\n{"\n".join(map(str, self.meals))}"

class Menu(object):
    def __init__(self, http_client, date=""):
        self.date = date
        self.http_client = http_client
        self.raw = self.get_menu(date=date)
        self.days = [Day(self, http_client, day) for day in self.raw]
        self.current_date = date if date else self.days[0].day_date
    
    def get_menu(self, date="", navigation=0):
        obj = self.http_client.apiGet("Reservation", params={"lastdate": date, "navigation": navigation})
        return obj.json()
    
    def refresh_menu(self, date="", navigation=0):
        obj = self.get_menu(date=date, navigation=navigation)
        self.raw = obj
        self.days = [Day(self, self.http_client, day) for day in self.raw]
    
    def getPrice(self, check_reservation=False):
        return sum(x.getPrice(check_reservation=check_reservation) for x in self.days)
    
    def __str__(self):
        return f'{"\n====================\n".join(map(str, self.days))}\n\
        total price: {self.getPrice()}\n\
        remaining price: {self.getPrice(check_reservation=True)}'