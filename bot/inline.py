
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from .general import generalInlineHandlerClass

class menucommandFilterToggleHandler(generalInlineHandlerClass):
    button_text = {True: "مشاهده منو با فیلترها", False: "مشاهده منو بدون فیلترها"}
    def __init__(self, database):
        super().__init__(database, pattern="menucommand_togglefilter")
    
    async def callback(self, update, context, interface):
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton(
                self.button_text[interface.menu.enable_filters],
                callback_data="menucommand_togglefilter")
        ]])
        
        interface.menu.enable_filters = not interface.menu.enable_filters
        await update.callback_query.message.edit_text(f"{interface.menu}",reply_markup=keyboard)