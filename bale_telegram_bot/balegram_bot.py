import functools

from bale_telegram_bot.api_handler.telethon_handler import *
from bale_telegram_bot.bot import Bot
from balebot.utils.logger import Logger
from balebot.filters import *
from balebot.handlers import *
from balebot.models.messages import *
from config import BotConfig
from constants import *
from bale_telegram_bot.callbacks import *

my_logger = Logger.get_logger()
balegram_bot = Bot()

loop = balegram_bot.loop
bot = balegram_bot.bot
updater = balegram_bot.updater
dispatcher = balegram_bot.dispatcher


@dispatcher.command_handler([Command.start])
def conversation_starter(bot, update):
    general_message = TextMessage(BotMessage.greeting)
    kwargs = {}
    bot.respond(update, general_message)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TextFilter(), checking_session)
    ])


def checking_session(bot, update):
    phone = update.get_effective_message().text
    # future = loop.create_task(check_session(phone))
    future = asyncio.ensure_future(check_session(phone))
    future.add_done_callback(functools.partial(check_session_done, update, phone))


def check_session_done(update, phone, future):
    result = future.result()
    print(result)
    authorized = result[1]
    client = result[0]
    dispatcher.set_conversation_data(update, ConversationData.client, client)
    dispatcher.set_conversation_data(update, ConversationData.phone, phone)
    if not authorized:
        asyncio.ensure_future(sending_code_request(client, phone))
        message = TextMessage(BotMessage.enter_received_code)
        kwargs = {}
        bot.respond(update, message)
        dispatcher.register_conversation_next_step_handler(update, [
            MessageHandler(TextFilter(), sign_in_code)
        ])
    else:
        showing_menu(bot, update)


def sign_in_code(bot, update):
    code = update.get_effective_message().text
    client = dispatcher.get_conversation_data(update, ConversationData.client)
    phone = dispatcher.get_conversation_data(update, ConversationData.phone)
    future = asyncio.ensure_future(sign_in_without_pass(client, phone, code))
    future.add_done_callback(functools.partial(sign_in_without_pass_done, bot, update))


def sign_in_without_pass_done(bot, update, future):
    result = future.result()
    if result:
        showing_menu(bot, update)


def showing_menu(bot, update):
    general_message = TextMessage(BotMessage.choose_from_menu)
    btn_list = [
        TemplateMessageButton(ButtonMessage.show_me, ButtonMessage.show_me, ButtonAction.default),
        TemplateMessageButton(ButtonMessage.sending_message, ButtonMessage.sending_message, ButtonAction.default)
    ]
    message = TemplateMessage(general_message, btn_list)
    kwargs = {}
    bot.respond(update, message)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TemplateResponseFilter(keywords=[ButtonMessage.show_me]), show_me),
        MessageHandler(TemplateResponseFilter(keywords=[ButtonMessage.sending_message]), ask_username)
    ])


def show_me(bot, update):
    client = dispatcher.get_conversation_data(update, ConversationData.client)
    future = asyncio.ensure_future(get_me_info(client))
    future.add_done_callback(functools.partial(get_me_info_done, bot, update))


def get_me_info_done(bot, update, future):
    me_info = future.result()
    general_message = TextMessage(me_info)
    btn_list = [
        TemplateMessageButton(ButtonMessage.return_to_main_menu, ButtonMessage.return_to_main_menu,
                              ButtonAction.default)
    ]
    message = TemplateMessage(general_message, btn_list)
    bot.respond(update, message)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TemplateResponseFilter(keywords=[ButtonMessage.return_to_main_menu]), showing_menu)
    ])


def ask_username(bot, update):
    general_message = TextMessage(BotMessage.enter_username_to_send_message)
    btn_list = [
        TemplateMessageButton(ButtonMessage.return_to_main_menu, ButtonMessage.return_to_main_menu,
                              ButtonAction.default)
    ]
    message = TemplateMessage(general_message, btn_list)
    bot.respond(update, message)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TextFilter(), asking_message),
        MessageHandler(TemplateResponseFilter(keywords=[ButtonMessage.return_to_main_menu]), showing_menu)
    ])


def asking_message(bot, update):
    username = update.get_effective_message().text
    dispatcher.set_conversation_data(update, ConversationData.username, username)
    general_message = TextMessage(BotMessage.enter_message_to_send_message)
    btn_list = [
        TemplateMessageButton(ButtonMessage.return_to_main_menu, ButtonMessage.return_to_main_menu,
                              ButtonAction.default)
    ]
    message = TemplateMessage(general_message, btn_list)
    bot.respond(update, message)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TextFilter(), sending_message),
        MessageHandler(TemplateResponseFilter(keywords=[ButtonMessage.return_to_main_menu]), showing_menu)
    ])


def sending_message(bot, update):
    message_to_send = update.get_effective_message().text
    client = dispatcher.get_conversation_data(update, ConversationData.client)
    username = dispatcher.get_conversation_data(update, ConversationData.username)
    print(username)
    print(client)
    future = asyncio.ensure_future(send_message(client, username, message_to_send))
    future.add_done_callback(functools.partial(send_message_done, bot, update))


def send_message_done(bot, update, future):
    result = future.result()
    print(result)
    if not result:
        return
    general_message = TextMessage(BotMessage.message_sent)
    btn_list = [
        TemplateMessageButton(ButtonMessage.return_to_main_menu, ButtonMessage.return_to_main_menu,
                              ButtonAction.default)
    ]
    message = TemplateMessage(general_message, btn_list)
    bot.respond(update, message)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TemplateResponseFilter(keywords=[ButtonMessage.return_to_main_menu]), showing_menu)
    ])


updater.run()
