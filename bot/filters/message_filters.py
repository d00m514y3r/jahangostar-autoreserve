from telegram.ext import filters

class filterListFilter(filters.MessageFilter):
    def filter(self, message):
        return message.text in ("بر اساس روز", 'بر اساس وعده', 'بر اساس اسم غذا')

class mealListFilter(filters.MessageFilter):
    def filter(self, message):
        return message.text in ("صبحانه", "ناهار", "شام", "افطار", "سحری")

class dayListFilter(filters.MessageFilter):
    def filter(self, message):
        return message.text in ("شنبه","یکشنبه","دوشنبه","سه شنبه","چهارشنبه","پنجشنبه","جمعه")

class inversionListFilter(filters.MessageFilter):
    def filter(self, message):
        return message.text in ("هر غذایی که از این فیلتر عبور کند رزرو [میشود]",
            "هر غذایی که از این فیلتر عبور کند رزرو [نمیشود]")

class filterListIndexCheckFilter(filters.MessageFilter):
    def filter(self, message):
        try:int(message.text);return True
        except: return False

filter_index_f = filterListIndexCheckFilter()
filter_f = filterListFilter()
meal_f = mealListFilter()
day_f = dayListFilter()
inversion_f = inversionListFilter()