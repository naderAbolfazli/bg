from config import BotConfig
from constants import UserData, LogMessage


def step_success(response, user_data):
    user_data = user_data[UserData.kwargs]
    user_peer = user_data[UserData.user_peer]
    step_name = user_data[UserData.step_name]
    my_logger = user_data[UserData.logger]
    my_logger.info(LogMessage.successful_step_message_sending,
                   extra={UserData.user_id: user_peer.peer_id, UserData.step_name: step_name, "tag": "info"})


def step_failure(response, user_data):
    user_data = user_data[UserData.kwargs]
    user_peer = user_data[UserData.user_peer]
    step_name = user_data[UserData.step_name]
    my_logger = user_data[UserData.logger]
    bot = user_data[UserData.bot]
    message = user_data[UserData.message]
    user_data[UserData.attempt] += 1
    if user_data[UserData.attempt] < BotConfig.resending_max_try:
        bot.send_message(message, user_peer, step_success, step_failure)
        return
    my_logger.error(LogMessage.failed_step_message_sending,
                    extra={UserData.user_id: user_peer.peer_id, UserData.step_name: step_name, "tag": "info"})

