import api
import logging
import tomllib
from telegram.ext import ApplicationBuilder
from bot import (
    signin,
    menuCommandHandler,
    signoutCommandHandler
)

import sqlite3
from db import dbClass

with open("config.toml", "rb") as f:
    config = tomllib.load(f)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

try: proxy = config["proxy"]
except KeyError: proxy=None

db = dbClass(config["database_name"])

signin_handler = signin.handlerClass(db, api.apiInterface).getHandler()
menu_handler = menuCommandHandler(db).getHandler()
signout_handler = signoutCommandHandler(db).getHandler()

application = ApplicationBuilder().token(config["token"])
application.proxy(proxy).get_updates_proxy(proxy)
application = application.build()

application.add_handler(signin_handler)
application.add_handler(signout_handler)
application.add_handler(menu_handler)

application.run_polling()