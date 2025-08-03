from telegram.ext import (
    CommandHandler,
    # ConversationHandler, 
    # MessageHandler, 
    # filters
)

class menuCommandHandler(object):   
    def __init__(self, database):
        self.database = database
        self.handler = CommandHandler("menu", self.menu)

    def getHandler(self):
        return self.handler
    
    async def menu(self, update, context):
        interface = context.user_data["interface"]
        if not interface.menu:
            interface.generateMenu()
        await update.message.reply_text(f"here's your menu:\n{interface.menu}")
