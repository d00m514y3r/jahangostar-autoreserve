from telegram.ext import MessageHandler, filters
from ..general import generalMessageHandlerClass
from .message_filters import filter_index_f
import json

class removeFilterHandler(generalMessageHandlerClass):
    class state:
        CHOOSE_FILTER = 1
    def __init__(self, database, fallback):
        self.state_dict = {
            self.state.CHOOSE_FILTER: [MessageHandler(filter_index_f, self.choose_type)],
        }        
        super().__init__(database, "deletefilter")

    async def deletefilter(self, update, context):
        if not context.user_data["filters"]:
            await update.message.reply_text(self.database.texts.NO_FILTER_FOUND)
            return -1
        
        f_list = [f"{i+1} ➡️ {x}" for i, x in enumerate(context.user_data["filters"])]
        await update.message.reply_text(f"filters:\n{'\n'.join(f_list)}")
        await update.message.reply_text(self.database.texts.DELETEFILTER_SEND_INDEX)
        return self.state.CHOOSE_FILTER
    
    async def choose_type(self, update, context):
        i = int(update.message.text)
        if not (1 <= i <= len(context.user_data["filters"])):
            await update.message.reply_text(self.database.texts.INVALID_INPUT)
            return self.state.CHOOSE_FILTER
        
        i -= 1
        context.user_data["filters"].pop(i)
        self.database.update_filters(
            context.user_data["user_id"],
            json.dumps([x.as_dict() for x in context.user_data["filters"]]))
        await update.message.reply_text(self.database.texts.DELETEFILTER_SUCCESS)
        return -1
