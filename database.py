#!/usr/bin/env python

"""create database."""

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class Category(Base):
    """Table category."""

    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)

    @property
    def serialize(self):
        """Return object data in easily serializeable format."""
        return {
            'name': self.name,
            'id': self.id,
        }


class Item(Base):
    """Table item."""

    __tablename__ = 'item'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(400))
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    time = Column(Integer)

    @property
    def serialize(self):
        """Return object data in easily serializeable format."""
        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,
            'category_id': self.category_id,
            'time': self.time
        }


engine = create_engine('sqlite:///catelog.db')

Base.metadata.create_all(engine)
