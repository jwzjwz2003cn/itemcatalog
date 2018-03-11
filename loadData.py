from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
 
from database_setup import Category, Base, Item, User
 
engine = create_engine('sqlite:///catalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine
 
DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# Create dummy user
User1 = User(name="Frank Ji", email="jwzjwz2003cn@gmail.com",
             picture='https://lh3.googleusercontent.com/-pGvlqfwMTLo/Upz97rWN2GI/AAAAAAAAABc/3qc3rfyHvvQe1SgnQ9FbxCbVBt2_D6hlgCEwYBhgL/w140-h140-p/10baaa4c-0c86-4043-b37f-8a7aa902810c')
session.add(User1)
session.commit()

#Add Categories
category1 = Category(name = "Shoes")

session.add(category1)
session.commit()

category2 = Category(name = "Toys")

session.add(category2)
session.commit()


#Add Items
item1 = Item(name = "yeezy boost 350 v2 zebra", description = """The Adidas Yeezy Boost 350 V2 Zebra is easily one \
																		of the most coveted and hyped sneakers on the market to date. \
																		It has a striking black and white pattern that can make any outfit stand out from the rest. \
																		Aside from all the aesthetics, its utmost comfort is one of the main factors why many \
																		consumers have always wanted a pair of these hard-to-get kicks. It is undoubtedly an expensive, \
																		hard to acquire shoe like any other Yeezys, but such characteristics make it even \
																		more desirable to a huge number of consumers.""", category = category1, user_id = 1)

session.add(item1)
session.commit()


item2 = Item(name = "NERF N-Strike Elite Sonic Ice", description = """Take your N-Strike battling to the next level with the Rampage blaster! With a 25-dart drum, \
																			  the Rampage blaster gives you an incredible rapid-fire blitz, firing revolutionary Elite Darts at a range of 75 feet. \
																			  Release a storm of darts at your target by sliding the slam fire handle repeatedly while you hold down the trigger! \
																			  The drum works with other Clip System blasters (sold separately), and the Elite Darts work with any Elite blaster \
																			  and most original N-Strike blasters (sold separately). For the final word in today\'s blaster technology, \
																			  you need the slam-fire blasting of the Rampage blaster! Includes Rampage body, drum connector, \
																			  25-dart drum magazine, 25 Elite Darts and instructions""", category = category2, user_id = 1)

session.add(item2)
session.commit()





print "added items!"

