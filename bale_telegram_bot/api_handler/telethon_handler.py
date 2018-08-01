import asyncio
import threading

from telethon import TelegramClient, sync
from telethon.errors import SessionPasswordNeededError

api_id = 480179
api_hash = "f023ed3b03bac73fbd43414ead701798"


async def check_session(user_id, phone):
    client = TelegramClient("sessions/" + user_id+"-"+phone, api_id, api_hash)
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
    except SessionPasswordNeededError:
        return False
    return True


async def sign_in_with_pass(client, password):
    try:
        await client.sign_in(password=password)
    except Exception:
        return None
    return client.get_me()


async def get_me_info(client):
    return await client.get_me()


async def send_message(client, username, message):
    return await client.send_message(entity=username, message=message)


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
