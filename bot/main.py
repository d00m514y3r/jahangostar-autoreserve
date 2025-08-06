from telegram.ext import ApplicationBuilder
from .signin import signinHandler
from .commands import (
    menuCommandHandler,
    signoutCommandHandler,
    nextmenuCommandHandler,
    reserveallCommandHandler,
    unreserveallCommandHandler
)

def get_bot_application(token, proxy, db, api):
    
    signin_handler = signinHandler(db, api).getHandler()
    menu_handler = menuCommandHandler(db).getHandler()
    nextmenu_handler = nextmenuCommandHandler(db).getHandler()
    signout_handler = signoutCommandHandler(db).getHandler()
    reserveall_handler = reserveallCommandHandler(db).getHandler()
    unreserveall_handler = unreserveallCommandHandler(db).getHandler()

    application = ApplicationBuilder().token(token)
    if proxy:
        application.proxy(proxy).get_updates_proxy(proxy)
    
    application = application.build()

    application.add_handler(signin_handler)
    application.add_handler(signout_handler)
    application.add_handler(menu_handler)
    application.add_handler(nextmenu_handler)
    application.add_handler(reserveall_handler)
    application.add_handler(unreserveall_handler)

    return application