import asyncio
import functools

from bot.api_handler.telethon_handler import *
from bot.base_bot import Bot
from bot.callbacks import profpic_upload_success, profpic_upload_failure, final_download_success, \
    send_message_done, step_success, step_failure
from bot.db_handler import check_user, add_registered_session, remove_current_session
from bot.models.base import Base, engine
from python_bale_bot.filters import *
from python_bale_bot.handlers import *
from python_bale_bot.models.messages import *
from python_bale_bot.utils.logger import Logger
from constants import *

my_logger = Logger.get_logger()
balegram_bot = Bot()

loop = balegram_bot.loop
bot = balegram_bot.bot
updater = balegram_bot.updater
dispatcher = balegram_bot.dispatcher

# print(Base.metadata.tables)
Base.metadata.create_all(engine)


######################## send_message ###################
def send_message(message, peer, step, succedent_message=None):
    kwargs = {UserData.user_peer: peer, UserData.step_name: step, UserData.succedent_message: succedent_message,
              UserData.message: message, UserData.attempt: SendingAttempt.first, UserData.bot: bot}
    bot.send_message(message=message, peer=peer, success_callback=step_success, failure_callback=step_failure,
                     kwargs=kwargs)


######################## conversation ###################

@dispatcher.command_handler([Command.start])
def conversation_starter(bot, update):
    user_id = update.get_effective_user().peer_id
    account = check_user(user_id)
    if account:
        future = asyncio.ensure_future(check_session(user_id, account.phone))
        future.add_done_callback(functools.partial(check_session_done, update, account.phone))
        send_message(TextMessage(BotMessage.please_wait), update.get_effective_user(), Step.conversation_starter)
        return
    general_message = TextMessage(BotMessage.greeting)
    send_message(general_message, update.get_effective_user(), Step.conversation_starter)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TextFilter(pattern=Patterns.phone_number_pattern), checking_session),
        MessageHandler(DefaultFilter(), wrong_phone_number)
    ])


def wrong_phone_number(bot, update):
    general_message = TextMessage(BotMessage.wrong_phone_number)
    send_message(general_message, update.get_effective_user(), Step.wrong_phone_number)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TextFilter(pattern=Patterns.phone_number_pattern), checking_session),
        MessageHandler(DefaultFilter(), wrong_phone_number)
    ])


def checking_session(bot, update):
    phone = update.get_effective_message().text
    # future = loop.create_task(check_session(phone))
    future = asyncio.ensure_future(check_session(update.get_effective_user().peer_id, phone))
    future.add_done_callback(functools.partial(check_session_done, update, phone))
    message = TextMessage(BotMessage.please_wait)
    send_message(message, update.get_effective_user(), Step.checking_session)


def check_session_done(update, phone, future):
    result = future.result()
    authorized = result[1]
    client = result[0]
    dispatcher.set_conversation_data(update, ConversationData.client, client)
    dispatcher.set_conversation_data(update, ConversationData.phone, phone)
    if not authorized:
        asyncio.ensure_future(sending_code_request(client, phone))
        message = TextMessage(BotMessage.enter_received_code)
        send_message(message, update.get_effective_user(), Step.check_session_done)
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
    message = TextMessage(BotMessage.please_wait)
    send_message(message, update.get_effective_user(), Step.sign_in_code)


def sign_in_without_pass_done(bot, update, future):
    phone = dispatcher.get_conversation_data(update, ConversationData.phone)
    result = future.result()
    if result == 1:
        add_registered_session(update.get_effective_user().peer_id, phone)
        showing_menu(bot, update)
    elif result == 0:
        sign_in_pass(bot, update)
    elif result == -1:
        pass


def ask_pass(bot, update):
    message = TextMessage(BotMessage.enter_your_pass)
    send_message(message, update.get_effective_user(), Step.ask_pass)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TextFilter(), sign_in_pass)
    ])


def sign_in_pass(bot, update):
    password = update.get_effective_message().text
    client = dispatcher.get_conversation_data(update, ConversationData.client)
    future = asyncio.ensure_future(sign_in_with_pass(client, password))
    future.add_done_callback(functools.partial(sign_in_with_pass_done, bot, update))


def sign_in_with_pass_done(bot, update, future):
    result = future.result()
    if result:
        showing_menu(bot, update)
    else:
        pass


def showing_menu(bot, update):
    general_message = TextMessage(BotMessage.choose_from_menu)
    btn_list = [
        TemplateMessageButton(ButtonMessage.show_me, ButtonMessage.show_me, ButtonAction.default),
        TemplateMessageButton(ButtonMessage.sending_message, ButtonMessage.sending_message, ButtonAction.default),
        TemplateMessageButton(ButtonMessage.receive_message, ButtonMessage.receive_message, ButtonAction.default),
        TemplateMessageButton(ButtonMessage.show_open_conversation, ButtonMessage.show_open_conversation,
                              ButtonAction.default),
        TemplateMessageButton(ButtonMessage.logout, ButtonMessage.logout, ButtonAction.default)
    ]
    message = TemplateMessage(general_message, btn_list)
    send_message(message, update.get_effective_user(), Step.checking_session)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TemplateResponseFilter(keywords=[ButtonMessage.show_me]), show_me),
        MessageHandler(TemplateResponseFilter(keywords=[ButtonMessage.sending_message]), ask_username_for_send),
        MessageHandler(TemplateResponseFilter(keywords=[ButtonMessage.receive_message]), ask_username_for_receive),
        MessageHandler(TemplateResponseFilter(keywords=[ButtonMessage.show_open_conversation]),
                       showing_open_conversation),
        MessageHandler(TemplateResponseFilter(keywords=[ButtonMessage.logout]), logout)
    ])


def logout(bot, update):
    remove_current_session(update.get_effective_user().peer_id)
    conversation_starter(bot, update)


def show_me(bot, update):
    client = dispatcher.get_conversation_data(update, ConversationData.client)
    future = asyncio.ensure_future(get_me_info(client, update.get_effective_user().peer_id))
    future.add_done_callback(functools.partial(get_me_info_done, bot, update))


def get_me_info_done(bot, update, future):
    user = future.result()
    user_peer = update.get_effective_user()
    text_message = TextMessage(BotMessage.me_info.format(user.first_name, user.last_name, user.username, user.phone))
    kwargs = {UserData.user_peer: user_peer, UserData.text_message: text_message, UserData.bot: bot,
              UserData.logger: my_logger}
    bot.upload_file(file="media/profilePicture/{}.jpg".format(user_peer.peer_id), file_type="file",
                    success_callback=profpic_upload_success, failure_callback=profpic_upload_failure, kwargs=kwargs)
    bot.respond(update, BotMessage.photo_downloading)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TemplateResponseFilter(keywords=[ButtonMessage.return_to_main_menu]), showing_menu)
    ])


def ask_username_for_send(bot, update):
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


def ask_username_for_receive(bot, update):
    general_message = TextMessage(BotMessage.enter_username_to_send_message)
    btn_list = [
        TemplateMessageButton(ButtonMessage.return_to_main_menu, ButtonMessage.return_to_main_menu,
                              ButtonAction.default)
    ]
    message = TemplateMessage(general_message, btn_list)
    bot.respond(update, message)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TextFilter(), receiving_message),
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
        MessageHandler(TextFilter(), sending_text_message),
        MessageHandler(PhotoFilter(), sending_photo_message),
        MessageHandler(TemplateResponseFilter(keywords=[ButtonMessage.return_to_main_menu]), showing_menu)
    ])


def sending_text_message(bot, update):
    message_to_send = update.get_effective_message().text
    client = dispatcher.get_conversation_data(update, ConversationData.client)
    username = dispatcher.get_conversation_data(update, ConversationData.username)
    future = asyncio.ensure_future(send_message(client, username, message_to_send))
    future.add_done_callback(functools.partial(send_message_done, bot, update))
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TemplateResponseFilter(keywords=[ButtonMessage.return_to_main_menu]), showing_menu)
    ])


def sending_photo_message(bot, update):
    user_id = update.body.sender_user.peer_id
    file_id = update.body.message.file_id
    caption_text = update.body.message.caption_text.text
    client = dispatcher.get_conversation_data(update, ConversationData.client)
    username = dispatcher.get_conversation_data(update, ConversationData.username)
    kwargs = {'client': client, 'username': username, 'bot': bot, 'update': update, 'text_message': caption_text}
    bot.download_file(file_id=file_id, user_id=user_id, file_type="photo", success_callback=final_download_success,
                      kwargs=kwargs)
    bot.respond(update, BotMessage.photo_uploading)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TemplateResponseFilter(keywords=[ButtonMessage.return_to_main_menu]), showing_menu)
    ])


def showing_open_conversation(bot, update):
    client = dispatcher.get_conversation_data(update, ConversationData.client)
    future = asyncio.ensure_future(get_dialogs(client))
    future.add_done_callback(functools.partial(get_dialogs_done, bot, update))


def get_dialogs_done(bot, update, future):
    dialogs = future.result()
    dialogs_string = ''.join([(dialog.name + ":" + str(dialog.draft) + "\n\n") for dialog in dialogs])
    general_message = TextMessage(dialogs_string)
    btn_list = [
        TemplateMessageButton(ButtonMessage.return_to_main_menu, ButtonMessage.return_to_main_menu,
                              ButtonAction.default)
    ]
    message = TemplateMessage(general_message, btn_list)
    send_message(message, update.get_effective_user(), Step.get_dialogs_done)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TemplateResponseFilter(keywords=[ButtonMessage.return_to_main_menu]), showing_menu)
    ])


def receiving_message(bot, update):
    username = update.get_effective_message().text
    client = dispatcher.get_conversation_data(update, ConversationData.client)
    future = asyncio.ensure_future(get_messages(client, username))
    future.add_done_callback(functools.partial(get_messages_done, bot, update))


def get_messages_done(bot, update, future):
    messages = future.result()
    messages_string = ''.join([(message[0] + ': ' + message[1] + "\n") for message in messages])
    general_message = TextMessage(messages_string)
    btn_list = [
        TemplateMessageButton(ButtonMessage.return_to_main_menu, ButtonMessage.return_to_main_menu,
                              ButtonAction.default)
    ]
    message = TemplateMessage(general_message, btn_list)
    send_message(message, update.get_effective_user(), Step.get_messages_done)
    dispatcher.register_conversation_next_step_handler(update, [
        MessageHandler(TemplateResponseFilter(keywords=[ButtonMessage.return_to_main_menu]), showing_menu)
    ])


##############################

# updater.run()
updater.start_webhook()
