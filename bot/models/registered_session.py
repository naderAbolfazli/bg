from dataclasses import dataclass, field, Field

from sqlalchemy import Column, Integer, String, Boolean, Table

from bot.models.base import Base


#
# class RegisteredSession(Base):
#     __tablename__ = "registered_session"
#     id = Column(Integer, primary_key=True)
#     user_id = Column(String, nullable=False)
#     phone = Column(String, nullable=False)
#     is_current = Column(Boolean)
#
#     def __init__(self, user_id, phone, is_current):
#         self.user_id = user_id
#         self.phone = phone
#         self.is_current = is_current


@dataclass
class RegisteredSession(Base):
    __tablename__: str = "registered_session"
    id: int = Column(Integer, primary_key=True)
    user_id: str = Column(String, nullable=False)
    phone: str = Column(String, nullable=False)
    is_current: bool = Column(Boolean)

# f= field(default='test')
# print(type(f.default))
# # print(type(Field.default.value))
# r = RegisteredSession()
# print(type(r))

# Table()