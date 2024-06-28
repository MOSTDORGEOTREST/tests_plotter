from sqlalchemy import Column, String, Integer
from db.database import Base


class Users(Base):
    __tablename__ = "users"

    username = Column(String(50), primary_key=True)
    password_hash = Column(String(60))


class Experiments(Base):
    __tablename__ = "experiments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    test_type = Column(String(100))
    link = Column(String(200))
    laboratory_number = Column(String(100))
    object_number = Column(String(50))
    description = Column(String(1000))
