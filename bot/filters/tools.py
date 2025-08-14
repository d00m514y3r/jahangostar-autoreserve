from .menu_filters import *

def load_from_database(obj):
    l = []
    for x in obj:
        match x["type"]:
            case "meal":
                l.append(mealFilter(x["meal"], invert=x["invert"]))
            case "day":
                l.append(dayFilter(x["day"], invert=x["invert"]))
            case "food":
                l.append(foodFilter(x["food"], invert=x["invert"]))
            case "self":
                l.append(selfFilter(x["self"], invert=x["invert"]))
    return l