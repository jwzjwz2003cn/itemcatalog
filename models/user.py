from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from models import Base


class User(Base):
    """
    User class represents the data model of the Google User
    Table

    Attributes:
        id (int): primary key of the table, generated by db
        name (String): The name of google account owner
        email(String): The gmail address of the google account owner
        picture(String): The url of the google account's profile picture
    """
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))