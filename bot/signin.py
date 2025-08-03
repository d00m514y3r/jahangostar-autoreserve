from telegram.ext import (
    CommandHandler,
    ConversationHandler, 
    MessageHandler, 
    filters
)
import json

class handlerClass(object):
    class state:
        USERNAME = 0
        PASSWORD = 1        
    def __init__(self, database, interface):
        self.database = database
        self.interfaceGenerator = interface
        self.handler = ConversationHandler(        
        entry_points=[
            CommandHandler("start", self.start)
        ],
        states = {
            self.state.USERNAME: [MessageHandler(filters.TEXT, self.username)],
            self.state.PASSWORD: [MessageHandler(filters.TEXT, self.password)]
        },
        fallbacks=[CommandHandler("start", self.start)]
    )

    def getHandler(self):
        return self.handler

    async def start(self, update, context):
        if "user_id" in context.user_data:
            await update.message.reply_text(f"login success! please use the commands:\n/menu")
            return ConversationHandler.END
        
        context.user_data["user_id"] = update.message.chat.id
        context.user_data["name"] = update.message.from_user.name
        context.user_data["is_authorized"] = False
        
        if user := self.database.get_user(update.message.chat.id):

            await update.message.reply_text(f"login success! please use the commands:\n/menu")
            interface = self.interfaceGenerator(
                username=user["self_username"],
                password=user["self_password"],
                cookie=json.loads(user["cookie"])
            )
            context.user_data["interface"] = interface
            context.user_data["is_authorized"] = True
            return ConversationHandler.END
        
        else:
            await update.message.reply_text("please send your username")
            return self.state.USERNAME

    async def username(self, update, context):
        context.user_data["self_username"] = update.message.text
        await update.message.reply_text("please send your password")
        return self.state.PASSWORD

    async def password(self, update, context):
        context.user_data["self_password"] = update.message.text
        try:
            interface = self.interfaceGenerator(
                username=context.user_data["self_username"],
                password=context.user_data["self_password"],
            )
            context.user_data["interface"] = interface
        except self.interfaceGenerator.loginError:
            #TODO
            pass
        else:
            self.database.create_user(
                user_id=context.user_data["user_id"],
                name=context.user_data["name"],
                self_username=context.user_data["self_username"],
                self_password=context.user_data["self_password"],
                is_verified=False,
                cookie=json.dumps(interface.http_client.getHttpClient().cookies.get_dict())
            )
            context.user_data["is_authorized"] = True
            await update.message.reply_text(f"login success! please use the commands:\n/menu")

        return ConversationHandler.END
