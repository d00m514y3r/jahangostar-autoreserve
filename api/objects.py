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
        self.parentMeal = parentMeal
        self.raw = obj
        self.id = obj["FoodId"]
        self.name = obj["FoodName"]
        self.SelfMenu = {x["SelfId"]: SelfService(self, x) for x in obj["SelfMenu"]}
        self.self_count = len(self.SelfMenu)
        self.food_state = obj["FoodState"]
        self.is_reserved = False
        if self.parentMeal.is_reserved == True:
            if self.id == self.parentMeal.raw["LastReserved"][0]["FoodId"]:
                self.is_reserved = True
        
    def __str__(self):
        if self.is_reserved:
            return f"  ✅ {self.name}\n{"\n".join(map(str, self.SelfMenu.values()))}"
        else:
            return f"  ❌ {self.name}\n{"\n".join(map(str, self.SelfMenu.values()))}"

    
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
        self.meal_name = obj["MealName"]
        self.date = obj["Date"]
        self.is_reserved = bool(obj["LastReserved"])

        self.FoodMenu = {x["FoodId"]:Food(self, http_client, x) for x in obj["FoodMenu"]}
        self.food_count = len(self.FoodMenu)
        
        self.service_selected = None
        self.food_selected = None

        if self.is_reserved:
            self.food_selected = self.FoodMenu[obj["LastReserved"][0]["FoodId"]]
            self.service_selected = self.food_selected.SelfMenu[obj["LastReserved"][0]["SelfId"]]
    
    def getTotalPrice(self):
        return sum([x.price for x in self.FoodMenu])
    
    def getRemainingPrice(self):
        if self.is_reserved or self.meal_state != 0:
            return 0
        else:
            price = sum([x.price if x.food_state == 2 else 0 for x in self.FoodMenu])
            return price

    def __str__(self):
        return f"⏰ {self.meal_name}\n{"\n".join(map(str, self.FoodMenu.values()))}"            
    
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
    
    def __str__(self):
        return f"🗓 {self.DayTitle}، {self.DayDate}\n{"\n".join(map(str, self.Meals))}"

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
        return "\n====================\n".join(map(str, self.Days))