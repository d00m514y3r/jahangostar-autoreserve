from telegram.ext import MessageHandler, filters
from ..general import generalMessageHandlerClass
import json

class removeFilterHandler(generalMessageHandlerClass):
    class state:
        CHOOSE_FILTER = 1
    def __init__(self, database, fallback):
        self.state_dict = {
            self.state.CHOOSE_FILTER: [MessageHandler(filters.TEXT, self.choose_type)],
        }        
        super().__init__(database, fallback, "deletefilter")

    async def deletefilter(self, update, context):
        f_list = [f"{i+1} ➡️ {x}" for i, x in enumerate(context.user_data["filters"])]
        await update.message.reply_text(f"filters:\n{'\n'.join(f_list)}")
        await update.message.reply_text(self.database.texts.DELETEFILTER_SEND_INDEX)
        return self.state.CHOOSE_FILTER
    
    async def choose_type(self, update, context):
        try: i = int(update.message.text)
        except: print(f"error {e}");return self.state.CHOOSE_FILTER
        if not (1 <= i <= len(context.user_data["filters"])):
            print(f"error");return self.state.CHOOSE_FILTER
        i -= 1
        context.user_data["filters"].pop(i)
        self.database.update_filters(
            context.user_data["user_id"],
            json.dumps([x.as_dict() for x in context.user_data["filters"]]))
        await update.message.reply_text(self.database.texts.DELETEFILTER_SUCCESS)
        return -1
