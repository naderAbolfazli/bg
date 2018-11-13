from telethon import TelegramClient, utils
from telethon.errors import SessionPasswordNeededError, PhoneNumberUnoccupiedError
import hashlib

from telethon.tl.types import User

from balebot.models.messages import TextMessage, PhotoMessage
from config import DbConfig

api_id = 480179
api_hash = "f023ed3b03bac73fbd43414ead701798"


async def check_session(user_id, phone):
    session_name = user_id + phone + DbConfig.db_hash_key
    session_name = hashlib.md5(session_name.encode('utf-8')).hexdigest()
    client = TelegramClient("sessions/" + session_name, api_id, api_hash)
    # client.get_messages()
    # client.build_reply_markup()
    await client.connect()
    # Ensure you're authorized
    authorized = await client.is_user_authorized()
    if authorized:
        return client, True
    else:
        return client, False


async def sending_code_request(client, phone):
    await client.send_code_request(phone)


async def sign_in_without_pass(client, phone, code):
    try:
        await client.sign_in(phone, code)
    except PhoneNumberUnoccupiedError:
        return -1
    except SessionPasswordNeededError:
        return 0
    return 1


async def sign_in_with_pass(client, password):
    try:
        await client.sign_in(password=password)
    except Exception:
        return None
    return True


async def get_me_info(client, user_id):
    me = await client.get_me()
    await client.download_profile_photo(me.username, file="media/profilePicture/" + user_id)
    return me


async def send_message(client, username, message, file=None):
    if not file:
        return await client.send_message(entity=username, message=message)
    elif file:
        return await client.send_message(entity=username, message=message, file=file)


async def get_dialogs(client):
    return await client.get_dialogs(limit=10)


async def get_messages(client, username):
    messages = client.iter_messages(username, limit=10)
    result = []
    # messages_it = AsyncGenerator
    async for message in messages:
        result.append((utils.get_display_name(message.sender), message.message))
    return result

#
# if __name__ == '__main__':
#     phone = "+989220592353"
# loop = asyncio.get_event_loop()
# asyncio.set_event_loop(loop)
# res = loop.run_until_complete(check_session(phone))
# cl = res[0]
# if not res[1]:
#     sending_code_request(cl, phone)
#     sign_in_without_pass(cl, phone, input('enter code'))
# print(get_me_info(cl))
# print(cl)
# send_message(cl, "nader93", "hello")
