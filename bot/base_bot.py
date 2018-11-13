import asyncio

from python_bale_bot.config import Config
from python_bale_bot.updater import Updater

from config import BotConfig


class Bot:
    Config.real_time_fetch_updates = True
    Config.continue_last_processed_seq = False
    Config.timeInterval = 1
    Config.updates_number = 3
    # Config.log_level = 0

    loop = asyncio.get_event_loop()

    updater = Updater(token=BotConfig.bot_token, user_id=1698782820)
    # Define dispatcher
    dispatcher = updater.dispatcher
    # Get bot
    bot = updater.dispatcher.bot

    # updater = Updater(token=BotConfig.bot_token,
    #                   loop=loop)
    # bot = updater.dispatcher.bot
    # dispatcher = updater.dispatcher
