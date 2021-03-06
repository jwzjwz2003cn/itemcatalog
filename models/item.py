from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from models.user import User
from models import Base


class Item(Base):
    """
    Item class represents the data model of the Item
    Table

    Attributes:
        id (int): primary key of the table, generated by db
        name (String): The name of the item
        Description (String): The description of the item
        category_id (int): The foreign key pointing to the category
                           entry in the Category table which the item
                           is belonging to
        user_id(String): The foreign key pointing to the user
                   from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()      entry in the User table who owns
                         the item.
        user(User): user entry referenced by the user_id foreign key in
              the User Table
    """
    __tablename__ = 'item'
    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    user = relationship(User)
    category_id = Column(Integer, ForeignKey('category.id'))
    user_id = Column(Integer, ForeignKey('user.id'))

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,
        }
