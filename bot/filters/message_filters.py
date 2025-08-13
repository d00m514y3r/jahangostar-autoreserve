from telegram.ext import filters

class filterListFilter(filters.MessageFilter):
    def filter(self, message):
        return message.text in ("بر اساس روز", 'بر اساس وعده', 'براساس اسم غذا')

class mealListFilter(filters.MessageFilter):
    def filter(self, message):
        return message.text in ("صبحانه", "ناهار", "شام", "افطار", "سحری")

class dayListFilter(filters.MessageFilter):
    def filter(self, message):
        return message.text in ("شنبه","یکشنبه","دوشنبه","سه شنبه","چهارشنبه","پنجشنبه","جمعه")

filter_f = filterListFilter()
meal_f = mealListFilter()
day_f = dayListFilter()