import logging

logger = logging.getLogger(__name__)

class generalMenuObject(object):
    def __init__(self, parent, raw, http_client=None):
        self.parent = parent
        self.raw = raw
        if http_client:
            self.http_client = http_client
        
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

class Food(generalMenuObject):
    def __init__(self, parent_meal, obj, http_client):
        super().__init__(parent_meal, obj, http_client)
        
        self.id = obj["FoodId"]
        self.name = obj["FoodName"]
        self.food_state = obj["FoodState"]
        self.reservation = False
        if self.parent.reservation:
            self.reservation = self.id == self.parent.reservation.food_id
        
        self.children = {x["SelfId"]: SelfService(self, x) for x in obj["SelfMenu"]}
        self.self_count = len(self.children)
        
    def __str__(self):
        emoji = {True: "✅", False: "❌"}
        
        return f"  {emoji[self.reservation]} {self.name}\n{"\n".join(map(str, self))}"

    def getPrice(self):
        return max(x.price for x in self)

    # TODO: delete function or move to Meal
    def change_reservation(self, count, self_id):
        if self.parent.meal_state != 0:
            logger.error(f"failed to change reservation status of {self} due to inactive meal" )
            return {"ok": False, "result": "meal not active"}
        
        payload = {
            "Date":self.parent.date,
            "MealId":self.parent.meal_id_day,
            "FoodId":self.id,
            "SelfId":self_id,
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

    def reserve(self, self_id):
        if self.reservation:
            logger.error(f"attempted to reserve {self} which is already reserved")
            return {"ok": False, "result": f"attempted to reserve {self} which is already reserved"}
        result = self.change_reservation(1, self_id)
        if result["ok"]:
            self.parent.reservation = Reservation(self, {"FoodId": self.id, "SelfId": self_id})
            self.reservation = True
            self.children[self_id].reservation = True
        return result
    
    def unreserve(self, self_id):
        if not self.reservation:
            logger.error(f"attempted to unreserve {self.id} which is not reserved")
            return {"ok": False, "result": f"attempted to unreserve {self} which is not reserved"}
        result = self.change_reservation(0, self_id)
        if result["ok"]:
            self.parent.reservation = None
            self.reservation = False
            self.children[self_id].reservation = False
        return result

class Meal(generalMenuObject):
    def __init__(self, parent_day, obj, http_client):
        super().__init__(parent_day, obj, http_client)

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

        self.children = {x["FoodId"]:Food(self, x, http_client) for x in obj["FoodMenu"]}
        self.food_count = len(self.children)
        
    def getPrice(self, skip_reserved):
        if self.food_count:
            if skip_reserved and self.reservation:
                return 0
            return max(food.getPrice() for food in self)
        return 0        
    def __str__(self):
        return f"⏰ {self.meal_name}\n{"\n".join(map(str, self))}"
    
class Day(generalMenuObject):
    def __init__(self, parent_menu, obj, http_client):
        super().__init__(parent_menu, obj, http_client)
        
        self.day_id = obj["DayId"]
        self.day_date = obj["DayDate"]
        self.day_title = obj["DayTitle"]
        self.day_state = obj["DayState"]
        self.day_state_title = obj["DayStateTitle"]
        self.children = [Meal(self, meal, http_client) for meal in obj["Meals"]]
    
    def getPrice(self, skip_reserved):
        return sum(x.getPrice(skip_reserved) for x in self)
    
    def __str__(self):
        return f"🗓 {self.day_title}، {self.day_date}\n{"\n".join(map(str, self))}"

class Menu(object):
    def __init__(self, http_client, date=""):
        self.date = date
        self.http_client = http_client
        self.raw = self.get_menu(date=date)
        self.days = [Day(self, day, http_client) for day in self.raw]
        self.current_date = date if date else self.days[0].day_date
    
    def get_menu(self, date="", navigation=0):
        obj = self.http_client.apiGet("Reservation", params={"lastdate": date, "navigation": navigation})
        return obj.json()
    
    def refresh_menu(self, date="", navigation=0):
        obj = self.get_menu(date=date, navigation=navigation)
        self.raw = obj
        self.days = [Day(self, day, self.http_client) for day in self.raw]
    
    def getPrice(self, skip_reserved=False):
        return sum(x.getPrice(skip_reserved=skip_reserved) for x in self.days)
    
    def __str__(self):
        return f'{"\n====================\n".join(map(str, self.days))}\n\
        total price: {self.getPrice()}\n\
        remaining price: {self.getPrice(skip_reserved=True)}'
    
    def __iter__(self):
        return iter(self.days)