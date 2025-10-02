from flask_login import UserMixin
from sqlalchemy import create_engine, Column, Integer, String
from db import app, Base, session, engine

class User(Base, UserMixin):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    firstname = Column(String(20), nullable=False)
    lastname = Column(String(20), nullable=False)
    email = Column(String(20), nullable=False, unique=True)
    password = Column(String(80), nullable=False)
    year = Column(String(80), nullable=True)