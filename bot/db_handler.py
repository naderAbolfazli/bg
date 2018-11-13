import hashlib
import os

from bot.models.base import Session
from bot.models.registered_session import RegisteredSession
from config import DbConfig

session = Session()


def check_user(user_id):
    query = session.query(RegisteredSession).filter(RegisteredSession.user_id == user_id,
                                                    RegisteredSession.is_current == True)
    return query.one_or_none()


def add_registered_session(user_id, phone):
    current = check_user(user_id)
    if current:
        current.is_current = False
        session.commit()
    registered_session = RegisteredSession(user_id=user_id, phone=phone, is_current=True)
    session.add(registered_session)
    session.commit()


def remove_current_session(user_id):
    registered_session = check_user(user_id)
    session_name = user_id + registered_session.phone + DbConfig.db_hash_key
    session_name = hashlib.md5(session_name.encode('utf-8')).hexdigest()
    os.remove("sessions/" + session_name+".session")
    session.delete(registered_session)
    session.commit()
