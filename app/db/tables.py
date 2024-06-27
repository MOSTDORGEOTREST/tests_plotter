from sqlalchemy import Column, String, Integer
from db.database import Base


class Users(Base):
    __tablename__ = "users"

    username = Column(String(50), primary_key=True)
    password_hash = Column(String(60))


class Tests(Base):
    __tablename__ = "tests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    test_type = Column(String(100))
    link = Column(String(200))
    description = Column(String)
