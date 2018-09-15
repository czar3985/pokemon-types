import sys

from sqlalchemy import Column, ForeignKey, Integer, String, Float, Boolean, PickleType
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()



class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)

    @property
    def serialize(self):
        return {
            'name': self.name,
            'id': self.id
            }


class Type(Base):
    __tablename__ = 'type'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)

    @property
    def serialize(self):
        return {
            'name': self.name,
            'id': self.id
            }


class Move(Base):
    __tablename__ = 'move'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)

    @property
    def serialize(self):
        return {
            'name': self.name,
            'id': self.id
            }


class Pokemon(Base):
    __tablename__ = 'pokemon'

    id = Column(Integer, nullable = False, primary_key = True)
    name = Column(String(50), nullable = False)
    description = Column(String(250), nullable = False)
    image = Column(String(250), nullable = False)
    height = Column(Integer, nullable = False)
    weight = Column(Float, nullable = False)
    is_mythical = Column(Boolean, nullable = False)
    is_legendary = Column(Boolean, nullable = False)
    evolution_before = Column(Integer, nullable = True)
    evolution_after_list = Column(PickleType, nullable = False)
    type_list = Column(PickleType, nullable = False)
    weakness_list = Column(PickleType, nullable = False)
    move_list = Column(PickleType, nullable = False)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'name': self.name,
            'pokedex_id': self.id,
            'description': self.description,
            'image': self.image,
            'height': self.height,
            'weight': self.weight,
            'is_mythical': self.is_mythical,
            'is_legendary': self.is_legendary,
            'category': self.category_id
            }


engine = create_engine('sqlite:///pokemon.db')
Base.metadata.create_all(engine)