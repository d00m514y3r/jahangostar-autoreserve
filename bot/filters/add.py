import json
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    CommandHandler,
    ConversationHandler, 
    MessageHandler, 
    filters
)

from ..general import generalMessageHandlerClass
from .message_filters import filter_f, meal_f, day_f, inversion_f
from .menu_filters import *

class filterAddHandler(generalMessageHandlerClass):
    class state:
        CHOOSE_FILTER_TYPE = 1
        APPLY_DAY = 11
        APPLY_MEAL = 12
        APPLY_FOOD = 13
        SELECT_INVERSION = 4

    class presets:
        meals = {"صبحانه": 1, "ناهار": 2, "شام": 3, "افطار": 4, "سحری": 5}
        days = {"شنبه":0,"یکشنبه":1,"دوشنبه":2,"سه شنبه":3,"چهارشنبه":4,"پنجشنبه":5,"جمعه":6}
        filter_type_keyboard = ReplyKeyboardMarkup(
            keyboard=[["بر اساس روز", 'بر اساس وعده', 'براساس اسم غذا'], ['لفو']],
            resize_keyboard=True)
        meal_filter_keyboard = ReplyKeyboardMarkup(
            keyboard=[["صبحانه", "ناهار", "شام", "افطار", "سحری"], ["لغو"]],
            resize_keyboard=True)
        day_filter_keyboard = ReplyKeyboardMarkup(
            keyboard=[["شنبه", "یکشنبه", "دوشنبه", "سه شنبه"],["چهارشنبه","پنجشنبه","جمعه"], ["لغو"]],
            resize_keyboard=True)
        inversion_keyboard = ReplyKeyboardMarkup(
            keyboard=[["هر غذایی که از این فیلتر عبور کند رزرو [میشود]"], ["هر غذایی که از این فیلتر عبور کند رزرو [نمیشود]"]],
            resize_keyboard=True
        )
        remove_keyboard = ReplyKeyboardRemove()

    def __init__(self, database, fallback):
        self.state_dict = {
            self.state.CHOOSE_FILTER_TYPE: [MessageHandler(filter_f, self.choose_type)],
            self.state.APPLY_MEAL: [MessageHandler(meal_f, self.apply_meal)],
            self.state.APPLY_DAY: [MessageHandler(day_f, self.apply_day)],
            self.state.SELECT_INVERSION: [MessageHandler(inversion_f, self.create_filter)]
        }        
        super().__init__(database, "addfilter")

    async def addfilter(self, update, context):
        context.user_data["temporary_filter"] = {}
        await update.message.reply_text(self.database.texts.FILTERADD_SELECT_FILTER,
            reply_markup=self.presets.filter_type_keyboard)
        return self.state.CHOOSE_FILTER_TYPE
    
    async def choose_type(self, update, context):
        match update.message.text:
            case "بر اساس وعده":
                await update.message.reply_text(self.database.texts.FILTERADD_SELECT_MEAL,
                    reply_markup=self.presets.meal_filter_keyboard)
                return self.state.APPLY_MEAL
            case "بر اساس روز":
                await update.message.reply_text(self.database.texts.FILTERADD_SELECT_DAY,
                    reply_markup=self.presets.day_filter_keyboard)
                return self.state.APPLY_DAY

    async def apply_meal(self, update, context):
        context.user_data["temporary_filter"] = \
            {"type": "meal", "meal": self.presets.meals[update.message.text], "inversion": None}
        await update.message.reply_text(self.database.texts.FILTERADD_SELECT_INVERSION,
            reply_markup=self.presets.inversion_keyboard)
        
        return self.state.SELECT_INVERSION
    
    async def apply_day(self, update, context):
        context.user_data["temporary_filter"] = \
            {"type": "day", "day": self.presets.days[update.message.text], "inversion": None}
        await update.message.reply_text(self.database.texts.FILTERADD_SELECT_INVERSION,
            reply_markup=self.presets.inversion_keyboard)
        
        return self.state.SELECT_INVERSION
    
    async def create_filter(self, update, context):
        inversion = (update.message.text == "هر غذایی که از این فیلتر عبور کند رزرو [نمیشود]")
        
        f = context.user_data["temporary_filter"]
        if f["type"] == "meal":
            f = mealFilter(f["meal"], invert=inversion)
        elif f["type"] == "day": 
            f = dayFilter(f["day"], invert=inversion)
        else:
            raise
        
        context.user_data["filters"].append(f)
        self.database.update_filters(
            context.user_data["user_id"],
            json.dumps([x.as_dict() for x in context.user_data["filters"]]))
        
        await update.message.reply_text(f"{self.database.texts.FILTERADD_SUCCESS}{f}",
            reply_markup=self.presets.remove_keyboard)
        return ConversationHandler.END