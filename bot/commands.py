from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove

from .general import generalCommandHandlerClass

class startCommandHandler(generalCommandHandlerClass):
    def __init__(self, database):
        super().__init__(database, "start", check_auth=False)

    async def start(self, update, context):
        if "is_authorized" in context.user_data and \
            context.user_data["is_authorized"]:
            await update.message.reply_text(self.database.texts.START_AUTH, reply_markup=ReplyKeyboardRemove())
        else:
            await update.message.reply_text(self.database.texts.START_NO_AUTH, reply_markup=ReplyKeyboardRemove())
        return -1

class menuCommandHandler(generalCommandHandlerClass):   
    def __init__(self, database):
        super().__init__(database, "menu")

    async def menu(self, update, context, interface):
        if not interface.menu:
            if interface.menu == None:
                interface.generateMenu()
            interface.menu.get_current_menu()
        
        interface.menu.enable_filters = False
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("مشاهده منو با فیلترها", callback_data="menucommand_togglefilter")
        ]])

        await update.message.reply_text(f"{self.database.texts.CURRENT_MENU}{interface.menu}",
        reply_markup=keyboard
        )

class nextmenuCommandHandler(generalCommandHandlerClass):   
    def __init__(self, database):
        super().__init__(database, "nextmenu")

    async def nextmenu(self, update, context, interface):
        if not interface.menu:
            if interface.menu == None:
                interface.generateMenu()
            # TODO: get next week instead of current
        try:
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

class creditCommandHandler(generalCommandHandlerClass):   
    def __init__(self, database):
        super().__init__(database, "credit")

    async def credit(self, update, context, interface):
        balance = interface.methods.getCredit()
        await update.message.reply_text(f"{self.database.texts.SHOW_CREDIT}{balance}")

class showfiltersCommandHandler(generalCommandHandlerClass):   
    def __init__(self, database):
        super().__init__(database, "showfilters")

    async def showfilters(self, update, context, interface):
        f_list = [f"{i+1} ➡️ {x}" for i, x in enumerate(context.user_data["filters"])]
        await update.message.reply_text(f"filters:\n{'\n'.join(f_list)}")