import logging
from .day import Day

logger = logging.getLogger(__name__)
    
class Menu(object):
    def __init__(self, http_client, raw=None):
        self.http_client = http_client
        self.raw = raw

        self.date = None
        self.days = []

        self.filters = []
    
    def __str__(self, filters=[]):
        return f'{"\n====================\n".join(x.__str__(filters=filters) for x in self)}\n\
        total price: {self.getPrice()}\n\
        remaining price: {self.getPrice(skip_reserved=True)}'
    
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
        if not self.date:
            # TODO: handle date not being set
            return False
        raise NotImplementedError
    
    def getPrice(self, skip_reserved=False):
        return sum(x.getPrice(skip_reserved=skip_reserved) for x in self.days)