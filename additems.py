from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Category, Base, Item

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

category1 = Category(name="Ball")

session.add(category1)
session.commit()

item1 = Item(name="Footbal", description="A football, soccer ball, or association football ball is the ball used in the sport of association football.",
                     category=category1)

session.add(item1)
session.commit()

item1 = Item(name="Basketball", description="A basketball is a spherical ball used in basketball games. Basketballs typically range in size from very small promotional items only a few inches in diameter to extra large balls nearly a foot in diameter used in training exercises.",
                     category=category1)

session.add(item1)
session.commit()

item1 = Item(name="Bandy ball", description="A bandy ball is a rubber ball used for playing bandy.",
                     category=category1)

session.add(item1)
session.commit()

item1 = Item(name="Baseball", description="A baseball is a ball used in the sport of the same name, baseball. The ball features a rubber or cork center, wrapped in yarn, and covered.",
                     category=category1)

session.add(item1)
session.commit()

category1 = Category(name="Board game")

session.add(category1)
session.commit()

item1 = Item(name="Chess", description="Chess is a two-player strategy board game played on a chessboard, a checkered gameboard with 64 squares arranged in an 88 grid.",
                     category=category1)

session.add(item1)
session.commit()

item1 = Item(name="Connection game", description="ChessA connection game is a type of abstract strategy game in which players attempt to complete a specific type of connection with their pieces.",
                     category=category1)

session.add(item1)
session.commit()

category1 = Category(name="Boring game")

session.add(category1)
session.commit()

print "added menu items!"