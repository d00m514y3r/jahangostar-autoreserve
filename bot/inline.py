
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from .general import generalInlineHandlerClass

class menucommandFilterToggleHandler(generalInlineHandlerClass):
    button_text = {False: "مشاهده منو با فیلترها", True: "مشاهده منو بدون فیلترها"}
    callbacks = {True: "menucommand_disablefilter", False: "menucommand_enablefilter"}
    def __init__(self, database):
        super().__init__(database, pattern="menucommand_.")
    
    async def callback(self, update, context, interface):
        use_filters = (update.callback_query.data == "menucommand_enablefilter")
        m = interface.menu.__str__(filters=context.user_data["filters"] if use_filters else None)
        
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton(
                self.button_text[use_filters],
                callback_data=self.callbacks[use_filters])
        ]])
        
        await update.callback_query.message.edit_text(m,reply_markup=keyboard)