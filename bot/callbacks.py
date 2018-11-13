import asyncio
import datetime
import os

from python_bale_bot.models.messages import TemplateMessageButton, TemplateMessage
from python_bale_bot.models.messages.photo_message import PhotoMessage
from python_bale_bot.models.messages.text_message import TextMessage
from python_bale_bot.utils.logger import Logger

from bot.api_handler.telethon_handler import send_message
from config import BotConfig
from constants import UserData, LogMessage, BotMessage, MimeType, SendingAttempt, ButtonMessage, ButtonAction

my_logger = Logger.get_logger()


def step_success(response, user_data):
    user_data = user_data[UserData.kwargs]
    user_peer = user_data[UserData.user_peer]
    step_name = user_data[UserData.step_name]
    my_logger.info(LogMessage.successful_step_message_sending,
                   extra={UserData.user_id: user_peer.peer_id, UserData.step_name: step_name, "tag": "info"})
    if user_data.get(UserData.succedent_message):
        bot = user_data[UserData.bot]
        step_name = user_data[UserData.step_name]
        succedent_message = user_data[UserData.succedent_message]
        kwargs = {UserData.user_peer: user_peer, UserData.step_name: step_name,
                  UserData.message: succedent_message, UserData.attempt: SendingAttempt.first,
                  UserData.logger: my_logger, UserData.bot: bot}
        bot.send_message(message=succedent_message, peer=user_peer, success_callback=step_success,
                         failure_callback=step_failure, kwargs=kwargs)


def step_failure(response, user_data):
    user_data = user_data[UserData.kwargs]
    user_peer = user_data[UserData.user_peer]
    step_name = user_data[UserData.step_name]
    bot = user_data[UserData.bot]
    message = user_data[UserData.message]
    user_data[UserData.attempt] += 1
    if user_data[UserData.attempt] < BotConfig.resending_max_try:
        bot.send_message(message=message, peer=user_peer, success_callback=step_success, failure_callback=step_failure,
                         kwargs=user_data)
        return
    my_logger.error(LogMessage.failed_step_message_sending,
                    extra={UserData.user_id: user_peer.peer_id, UserData.step_name: step_name, "tag": "error"})


def profpic_upload_success(response, user_data):
    file_id = str(user_data.get(UserData.file_id, None))
    file_url = str(user_data.get(UserData.url))
    access_hash = str(user_data.get(UserData.user_id, None))
    user_data = user_data[UserData.kwargs]
    my_logger = user_data[UserData.logger]
    bot = user_data[UserData.bot]
    user = user_data[UserData.user_peer]
    text_message = user_data[UserData.text_message]

    my_logger.info(LogMessage.successful_profpic_upload,
                   extra={UserData.file_url: file_url, "tag": "info"})
    file_size = os.path.getsize("media/profilePicture/{}.jpg".format(user.peer_id))
    photo_message = PhotoMessage(file_id=file_id, access_hash=access_hash,
                                 name=BotMessage.photo_name,
                                 file_size=file_size,
                                 mime_type=MimeType.image, caption_text=text_message,
                                 file_storage_version=1, thumb=None)
    btn_list = [
        TemplateMessageButton(ButtonMessage.return_to_main_menu, ButtonMessage.return_to_main_menu,
                              ButtonAction.default)
    ]
    message = TemplateMessage(photo_message, btn_list)
    kwargs = {UserData.user_peer: user, UserData.photo_message: message,
              UserData.report_attempt: SendingAttempt.first, UserData.logger: my_logger, UserData.bot: bot}
    bot.send_message(message, user, success_callback=profpic_success,
                     failure_callback=profpic_failure, kwargs=kwargs)
    os.remove("media/profilePicture/{}.jpg".format(user.peer_id))


def profpic_upload_failure(response, user_data):
    pass


def profpic_success(response, user_data):
    pass


def profpic_failure(response, user_data):
    pass


def final_download_success(result, user_data):
    print("download was successful : ", result)

    stream = user_data.get("byte_stream", None)
    now = str(datetime.datetime.now().time().strftime('%Y-%m-%d_%H:%M:%f'))
    print(user_data)
    print(type(stream))

    with open("media/{}.{}".format(now, "jpg"), "wb") as file:
        file.write(stream)
        file.close()

    user_data = user_data['kwargs']
    client = user_data['client']
    username = user_data['username']
    bot = user_data['bot']
    text_message = user_data['text_message']
    update = user_data['update']
    future = asyncio.ensure_future(send_message(client, username, text_message, "media/{}.{}".format(now, "jpg")))
    future.add_done_callback(send_message_done, bot, update)
    general_message = TextMessage(BotMessage.message_sent)
    btn_list = [
        TemplateMessageButton(ButtonMessage.return_to_main_menu, ButtonMessage.return_to_main_menu,
                              ButtonAction.default)
    ]
    message = TemplateMessage(general_message, btn_list)
    bot.respond(update, message)


def send_message_done(bot, update, future):
    result = future.result()
    print(result)
    # sent_flag = True
    # if not result:
    #     sent_flag = False

