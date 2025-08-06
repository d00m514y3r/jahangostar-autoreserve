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
            await update.message.reply_text(self.database.texts.NOT_SIGNED_IN)
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
        await update.message.reply_text(f"{self.database.texts.CURRENT_MENU}{interface.menu}")

class nextmenuCommandHandler(generalCommandHandlerClass):   
    def __init__(self, database):
        super().__init__(database, "nextmenu")

    async def nextmenu(self, update, context, interface):
        if not interface.menu:
            interface.generateMenu()
        try:
            interface.menu.refresh_menu(date=interface.menu.current_date, navigation=7)
            await update.message.reply_text(f"{self.database.texts.NEXT_MENU}{interface.menu}")
        except Exception as e:
            await update.message.reply_text(f"{self.database.texts.NEXT_MENU_NOT_AVAILABLE}{e}")


class signoutCommandHandler(generalCommandHandlerClass):   
    def __init__(self, database):
        super().__init__(database, "signout")

    async def signout(self, update, context, interface):
        self.database.delete_user(context.user_data["user_id"])
        context.user_data.clear()

        await update.message.reply_text(self.database.texts.SIGNOUT_SUCCESS)

class reserveallCommandHandler(generalCommandHandlerClass):
    def __init__(self, database):
        super().__init__(database, "reserveall")

    async def reserveall(self, update, context, interface):
        interface.generateMenu()
        interface.menu.refresh_menu(date=interface.menu.current_date, navigation=7)

        res = []
        for day in interface.menu:
            for meal in day:
                if meal.reservation:
                    print(f"{meal.meal_id_week} was ignored because it was reserved")
                    continue
                if meal.food_count != 1:
                    print(f"{meal.meal_id_week} was ignored because it had {meal.food_count} many food choices")
                    continue
                
                food = [x for x in meal.children.values()][0]
                if food.self_count != 1:
                    print(f"{meal.meal_id_week} was ignored because it didn't have a self-service choice")
                    continue
                result = food.reserve([x for x in food.children.values()][0].id)
                res.append(f"{result['ok']}: {food.parent}")

        await update.message.reply_text(f"reservation result:\n{'\n'.join(res)}")

class unreserveallCommandHandler(generalCommandHandlerClass):
    def __init__(self, database):
        super().__init__(database, "unreserveall")

    async def unreserveall(self, update, context, interface):
        interface.generateMenu()
        interface.menu.refresh_menu(date=interface.menu.current_date, navigation=7)

        res = []
        for day in interface.menu:
            for meal in day:
                if not meal.reservation:
                    print(f"{meal.meal_id_week} was ignored because it was not reserved")
                    continue
                food = meal.children[meal.reservation.food_id]
                for service in food:
                    if service.id == meal.reservation.self_id:
                        result = food.unreserve(service.id)
                        res.append(f"{result['ok']}: {meal}")
                        break
                else:
                    raise

        await update.message.reply_text(f"reservation result:\n{'\n'.join(res)}")