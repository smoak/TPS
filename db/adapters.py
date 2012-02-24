from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from db.entities import Base

Session = sessionmaker()

class DatabaseAdapter(object):
  """
  Database adapter that talks to a sql alchemy engine/session
  """
  
  def __init__(self, dbConfig):
    self.dbConfig = dbConfig
    self.engine = self.__createEngineFromConfig(self.dbConfig)
    Session.configure(bind=self.engine)
    self.session = Session()
    Base.metadata.create_all(self.engine)

  def __createEngineFromConfig(self, dbConfig):
    if dbConfig.databaseType == "sqlite":
      return create_engine("sqlite:///%s" % (dbConfig.databaseName), echo=True)
    else:
      return create_engine("%s://%s:%s@%s/%s" % (dbConfig.databaseType, dbConfig.userName, dbConfig.password, dbConfig.hostname, dbConfig.databaseName))
      
  def query(self, *args):
    return self.session.query(*args)
    
class DbConfig(object):
  databaseType = "sqlite"
  databaseName = ":memory:"