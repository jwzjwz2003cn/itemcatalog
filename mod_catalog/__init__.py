import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

CLIENT_ID = json.loads(
    open('client_secret.json', 'r').read())['web']['client_id']
# Connect to Database and create database session
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()
