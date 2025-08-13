from telegram.ext import (
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    filters
)

class generalInlineHandlerClass(object):
    def __init__(self, database, pattern):
        self.database = database
        self.entry_point = self.check_auth
        self.handler = CallbackQueryHandler(self.check_auth, pattern=pattern)

    async def check_auth(self, update, context):
        if "is_authorized" not in context.user_data \
        or not context.user_data["is_authorized"]:
            try:await update.callback_query.message.edit_text(self.database.texts.NOT_SIGNED_IN, reply_markup={})
            except:pass
            return None
        await update.callback_query.answer()
        interface = context.user_data["interface"]
        return await self.callback(update, context, interface)
    
    def getHandler(self):
        return self.handler


class generalCommandHandlerClass(object):
    def __init__(self, database, command, check_auth=True):
        self.database = database
        self.command = command
        if check_auth:
            self.handler = CommandHandler(command, self.check_auth)
        else:
            self.handler = CommandHandler(command, getattr(self, self.command))
    
    async def check_auth(self, update, context):
        if "is_authorized" not in context.user_data \
        or not context.user_data["is_authorized"]:
            await update.message.reply_text(self.database.texts.NOT_SIGNED_IN)
            return None
        interface = context.user_data["interface"]
        return await getattr(self, self.command)(update, context, interface)
    
    def getHandler(self):
        return self.handler

class cancelFilter(filters.MessageFilter):
    def filter(self, message):
        return message.text == "لفو"

cancel_f = cancelFilter()

class generalMessageHandlerClass(object):
    def __init__(self, database, command):
        self.database = database
        self.command = command
        self.entry_point = CommandHandler(command, self.check_auth)
        assert hasattr(self, "state_dict")

        self.handler = ConversationHandler(
            entry_points=[self.entry_point],
            states=self.state_dict,
            fallbacks=[
                MessageHandler(cancel_f, self.cancel),
                MessageHandler(filters.ALL, self.invalid_input)
                ]
        )
    async def invalid_input(self, update, context):
        await update.message.reply_text(self.database.texts.INVALID_INPUT)
    
    async def cancel(self, update, context):
        await update.message.reply_text(self.database.texts.CANCEL)
        return ConversationHandler.END


    async def check_auth(self, update, context):
        if "is_authorized" not in context.user_data \
        or not context.user_data["is_authorized"]:
            await update.message.reply_text(self.database.texts.NOT_SIGNED_IN)
            return None
        return await getattr(self, self.command)(update, context)
    
    def getHandler(self):
        return self.handler