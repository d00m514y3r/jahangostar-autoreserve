from telegram.ext import (
    CommandHandler,
    # ConversationHandler, 
    # MessageHandler, 
    # filters
)

class generalCommandHandlerClass(object):
    def __init__(self, database, command):
        self.database = database
        self.handler = CommandHandler(command, getattr(self, command))
    
    def getHandler(self):
        return self.handler

class menuCommandHandler(generalCommandHandlerClass):   
    def __init__(self, database):
        super().__init__(database, "menu")

    async def menu(self, update, context):
        if "is_authorized" not in context.user_data \
        or not context.user_data["is_authorized"]:
            await update.message.reply_text(f"you are not logged in! please login with /start")    
            return
        interface = context.user_data["interface"]
        if not interface.menu:
            interface.generateMenu()
        await update.message.reply_text(f"here's your menu:\n{interface.menu}")
