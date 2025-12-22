from telegram.ext import (
    CommandHandler,
    ConversationHandler, 
    MessageHandler, 
    filters
)
import json
from .filters import load_from_database

class signinHandler(object):
    class state:
        USERNAME = 0
        PASSWORD = 1        
    def __init__(self, database, interface, start_command):
        self.database = database
        self.interfaceGenerator = interface
        self.start_command = start_command.start
        self.handler = ConversationHandler(        
        entry_points=[
            CommandHandler("signin", self.signin)
        ],
        states = {
            self.state.USERNAME: [MessageHandler(filters.TEXT, self.username)],
            self.state.PASSWORD: [MessageHandler(filters.TEXT, self.password)]
        },
        fallbacks=[CommandHandler("start", self.start_command)]
    )

    def getHandler(self):
        return self.handler

    async def signin(self, update, context):
        if "user_id" in context.user_data:
            await update.message.reply_text(self.database.texts.SIGNIN_SUCCESS)
            return ConversationHandler.END
        
        context.user_data["user_id"] = update.message.chat.id
        context.user_data["name"] = update.message.from_user.name
        context.user_data["is_authorized"] = False
        
        if user := self.database.get_user(update.message.chat.id):

            interface = self.interfaceGenerator(
                username=user["self_username"],
                password=user["self_password"],
                cookie=json.loads(user["cookie"])
            )
            if not interface.http_client.cookie_login:
                self.database.update_cookie(
                    context.user_data["user_id"], 
                    json.dumps(interface.http_client.getHttpClient().cookies.get_dict())
                )
    
            context.user_data["interface"] = interface
            context.user_data["is_authorized"] = True
            context.user_data["filters"] = load_from_database(json.loads(user["filters"]))
            await update.message.reply_text(self.database.texts.SIGNIN_SUCCESS)
            await update.message.reply_text(self.database.texts.START_AUTH)
            return ConversationHandler.END
        
        else:
            await update.message.reply_text(self.database.texts.SEND_USERNAME)
            return self.state.USERNAME

    async def username(self, update, context):
        if "/start" in update.message.text:
            context.user_data.clear()
            return 2
        context.user_data["self_username"] = update.message.text
        await update.message.reply_text(self.database.texts.SEND_PASSWORD)
        return self.state.PASSWORD

    async def password(self, update, context):
        if "/start" in update.message.text:
            context.user_data.clear()
            return 2
        context.user_data["self_password"] = update.message.text
        try:
            interface = self.interfaceGenerator(
                username=context.user_data["self_username"],
                password=context.user_data["self_password"],
            )
            context.user_data["interface"] = interface
        except Exception as e:
            await update.message.reply_text(self.database.texts.SIGNIN_FAILED)
            context.user_data.clear()
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
            context.user_data["filters"] = []
            await update.message.reply_text(self.database.texts.SIGNIN_SUCCESS)
            await update.message.reply_text(self.database.texts.START_AUTH)

        return ConversationHandler.END
