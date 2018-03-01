from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Category, Base, Item, User

engine = create_engine('sqlite:///catelog.db')
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
User1 = User(name="Robo Barista", email="tinnyTim@udacity.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()

# Menu for UrbanBurger
category1 = Category(user_id=1, name="Ball")

session.add(category1)
session.commit()

item1 = Item(user_id=1, name="Soccer", description="soc desc",
                     category=category1)

session.add(item1)
session.commit()

item1 = Item(user_id=1, name="Basketball", description="bas desc",
                     category=category1)

session.add(item1)
session.commit()

category1 = Category(user_id=1, name="MAMA")

session.add(category1)
session.commit()

item1 = Item(user_id=1, name="MM", description="MM desc",
                     category=category1)

session.add(item1)
session.commit()

print "added menu items!"