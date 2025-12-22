import logging
import datetime
from .day import Day
from persiantools.jdatetime import JalaliDate, JalaliDateTime
logger = logging.getLogger(__name__)
    
class Menu(object):
    def __init__(self, http_client, raw=None):
        self.http_client = http_client
        self.raw = raw

        self.date = None
        self.days = []

        self.filters = []
    
    def __str__(self, filters=[]):
        if not (type(filters) is list):
            raise
        return f'{"\n====================\n".join(x.__str__(filters=filters) for x in self)}\n\
        total price: {self.getPrice(filters=filters)}\n\
        remaining price: {self.getPrice(filters=filters, skip_reserved=True)}'
    
    def __iter__(self):
        return iter(self.days)
    
    def __bool__(self):
        return bool(self.days)
    
    def get_menu(self, date, navigation):
        self.raw = self.http_client.apiGet("Reservation", params={"lastdate": date, "navigation": navigation}).json()
        self.days = [Day(self, day) for day in self.raw]
        self.date = self.days[0].day_date
    
    def get_current_menu(self):
        self.get_menu("", 0)
    
    def get_next_menu(self):
        x = JalaliDateTime.now()
        x -= datetime.timedelta(days=x.weekday())
        self.date = x.strftime("%Y/%m/%d")
        self.get_menu(date=self.date, navigation=7)
    
    def getPrice(self, filters=[], skip_reserved=False):
        if not (type(filters) is list):
            raise
        return sum(x.getPrice(filters=filters, skip_reserved=skip_reserved) for x in self.days)
    
    def reserve(self, filters=[]):
        if not (type(filters) is list):
            raise
        p = self.getPrice(filters=filters, skip_reserved=True)
        for day in self:
            for meal in day:
                if meal.reservation or meal.meal_state != 0:
                    print(f"meal {meal} is reserved or inavtive")
                f = None
                s = None
                for food in meal:
                    s_list = food.check_filters(filters)
                    if not s_list:
                        print(f"food {food} or self services did not pass filters")
                        continue 
                    if len(s_list) != 1:
                        print(f"more than one self service passed filters for food {food}")
                        continue 
                    if f != None:
                        print(f"more than one food passed filters for meal {meal}")
                        break
                    f = food
                    s = s_list[0]
                else:
                    x = f.reserve(s.id)
                    print(f"attempted to reserve {food} with {s.id}. res: {x['ok']}")
