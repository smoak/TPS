from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy.orm import mapper

metadata = MetaData()
items_table = Table('items', metadata, Column('id', Integer, primary_key=True), Column('type', Integer), Column('name', String), Column('height', Integer), Column('width', Integer))

Base = declarative_base()
class ItemEntity(Base):
  __tablename__ = 'items'
  
  id = Column(Integer, primary_key=True)
  name = Column(String)
  height = Column(Integer)
  width = Column(Integer)
  type = Column(Integer)
  
  def __init__(self, name, type, width, height):
    self.name = name
    self.type = type
    self.width = width
    self.height = height
    self.mapper = mapper(ItemEntity, items_table) 
    
  def __repr__(self):
    return "<ItemEntity('%s', Type='%d', '%d'x'%d')>" % (self.name, self.type, self.width, self.height)