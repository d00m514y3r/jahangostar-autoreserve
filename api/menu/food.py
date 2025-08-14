import logging

from .general import (
    generalMenuObject,
    Reservation,
    SelfService
)

logger = logging.getLogger(__name__)

class Food(generalMenuObject):
    def __init__(self, parent_meal, obj):
        super().__init__(parent_meal, obj)
        
        self.parent_menu = self.parent.parent.parent
        self.http_client = self.parent_menu.http_client

        self.id = obj["FoodId"]
        self.name = obj["FoodName"]
        self.food_state = obj["FoodState"]
        self.reservation = False
        if self.parent.reservation:
            self.reservation = self.id == self.parent.reservation.food_id
        
        self.children = {x["SelfId"]: SelfService(self, x) for x in obj["SelfMenu"]}
        self.self_count = len(self.children)
        
    def __str__(self, filters=[]):
        if filters:
            if not self.check_filters(filters):
                return 'filtered-food'

        emoji = {True: "✅", False: "❌"}
        return f"  {emoji[self.reservation]} {self.name}\n{"\n".join(x.__str__(filters) for x in self)}"

    def getPrice(self, filters):
        if filters:
            if not self.check_filters(filters):
                return 0
        return max(x.price for x in self)
    
    def check_filters(self, filters):
        s_list = []
        for f in filters:
            if f.type != "self":
                if not f.check(self):
                    return False
            else:
                for s in self:
                    if f.check(s):
                        s_list.append(s)
        return s_list

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