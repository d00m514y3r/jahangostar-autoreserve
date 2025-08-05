from telegram.ext import (
    CommandHandler,
)

class generalCommandHandlerClass(object):
    def __init__(self, database, command):
        self.database = database
        self.command = command
        self.handler = CommandHandler(command, self.check_auth)
    
    async def check_auth(self, update, context):
        if "is_authorized" not in context.user_data \
        or not context.user_data["is_authorized"]:
            await update.message.reply_text(f"you are not signed in! please sign in with /start")    
            return False
        interface = context.user_data["interface"]
        return await getattr(self, self.command)(update, context, interface)
    
    def getHandler(self):
        return self.handler

class menuCommandHandler(generalCommandHandlerClass):   
    def __init__(self, database):
        super().__init__(database, "menu")

    async def menu(self, update, context, interface):
        if not interface.menu:
            interface.generateMenu()
        else:
            interface.menu.refresh_menu()
        await update.message.reply_text(f"here's your menu:\n{interface.menu}")

class nextmenuCommandHandler(generalCommandHandlerClass):   
    def __init__(self, database):
        super().__init__(database, "nextmenu")

    async def nextmenu(self, update, context, interface):
        if not interface.menu:
            interface.generateMenu()
        try:
            interface.menu.refresh_menu(date=interface.menu.current_date, navigation=7)
            await update.message.reply_text(f"here's your menu:\n{interface.menu}")
        except Exception as e:
            await update.message.reply_text(f"next week's menu not available: {e}")


class signoutCommandHandler(generalCommandHandlerClass):   
    def __init__(self, database):
        super().__init__(database, "signout")

    async def signout(self, update, context, interface):
        self.database.delete_user(context.user_data["user_id"])
        context.user_data.clear()

        await update.message.reply_text(f"signout success! to sign in again use /start")    