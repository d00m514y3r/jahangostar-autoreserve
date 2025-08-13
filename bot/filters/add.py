from telegram.ext import (
    CommandHandler,
    ConversationHandler, 
    MessageHandler, 
    filters
)
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove

from ..general import generalMessageHandlerClass
from .menu_filters import mealFilter
import json

class filterTypeFilter(filters.MessageFilter):
    def filter(self, update, message):
        print(message)
        return True

class filterAddHandler(generalMessageHandlerClass):
    class state:
        CHOOSE_FILTER_TYPE = 1
        SEND_FILTER = 11
        APPLY_DAY = 111
        APPLY_MEAL = 112
        APPLY_FOOD = 113
        CANCEL = 0
    class presets:
        meals = {"صبحانه": 1, "ناهار": 2, "شام": 3, "افطار": 4, "سحری": 5}
        filter_type_keyboard = ReplyKeyboardMarkup(
            keyboard=[["بر اساس روز", 'بر اساس وعده', 'براساس اسم غذا'], ['لفو']],
            resize_keyboard=True)
        meal_filter_keyboard = ReplyKeyboardMarkup(
            keyboard=[["صبحانه", "ناهار", "شام", "افطار", "سحری"], ["لغو"]],
            resize_keyboard=True)
        remove_keyboard = ReplyKeyboardRemove()
        cancel_text = "لفو"
    def __init__(self, database, fallback):
        self.state_dict = {
            self.state.CHOOSE_FILTER_TYPE: [MessageHandler(filters.TEXT, self.choose_type)],
            self.state.APPLY_MEAL: [MessageHandler(filters.TEXT, self.apply_meal)],
        }        
        super().__init__(database, fallback, "addfilter")

    async def addfilter(self, update, context):
        await update.message.reply_text(self.database.texts.FILTERADD_SELECT_FILTER,
            reply_markup=self.presets.filter_type_keyboard)
        return self.state.CHOOSE_FILTER_TYPE
    
    async def choose_type(self, update, context):
        match update.message.text:
            case self.presets.cancel_text:
                await update.message.reply_text(self.database.texts.FILTERADD_CANCEL)
                return ConversationHandler.END
            case "بر اساس وعده":
                await update.message.reply_text(self.database.texts.FILTERADD_SELECT_MEAL,
                    reply_markup=self.presets.meal_filter_keyboard)
                return self.state.APPLY_MEAL
            case _:
                await update.message.reply_text(self.database.texts.FILTERADD_INVALID_INPUT,
                    reply_markup=self.presets.filter_type_keyboard)
                return self.state.CHOOSE_FILTER_TYPE

    async def apply_meal(self, update, context):
        if update.message.text in self.presets.meals:
            f = mealFilter(self.presets.meals[update.message.text])
            context.user_data["filters"].append(f)
            self.database.update_filters(
                context.user_data["user_id"],
                json.dumps([x.as_dict() for x in context.user_data["filters"]]))
            await update.message.reply_text(f"{self.database.texts.FILTERADD_SUCCESS}{f}", reply_markup=self.presets.remove_keyboard)
            return ConversationHandler.END
        else:
            await update.message.reply_text(self.database.texts.FILTERADD_INVALID_INPUT,
                reply_markup=self.presets.meal_filter_keyboard)
        return self.state.APPLY_MEAL
    

