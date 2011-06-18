import sqlalchemy, os


from sqlalchemy.orm import sessionmaker

from db.entities import ItemEntity

DB_FILE_NAME = "terraria.db"

class ItemRepository(object):
  def __init__(self):
    self.db_engine = sqlalchemy.create_engine('sqlite:///' + DB_FILE_NAME)
    Session = sessionmaker(bind=self.db_engine)
    self.session = Session()
    
  def getItemByType(self, itemType):
    item = self.session.query(ItemEntity).filter_by(type=itemType).first()
    return item