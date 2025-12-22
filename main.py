import logging
import tomllib
import bot
from api import apiInterface

from db import dbClass

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

with open("config.toml", "rb") as f:
    config = tomllib.load(f)

if "proxy" in config:
    proxy = config["proxy"]
else:
    proxy=None

if __name__ == "__main__":
    db = dbClass(config["database_name"])
    app = bot.get_bot_application(
        token=config["token"],
        proxy=proxy,
        db=db,
        api=apiInterface
        )
    app.run_polling()