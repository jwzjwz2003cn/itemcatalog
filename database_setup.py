from sqlalchemy import create_engine
from models import Base
from models.category import Category
from models.item import Item
from models.user import User

engine = create_engine('sqlite:///catalog.db')
Base.metadata.create_all(engine)
