from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from db.entities import Base

class DatabaseAdapter(object):
  """
  Database adapter that talks to a sql alchemy engine/session
  """
  
  def __init__(self, dbConfig):
    self.dbConfig = dbConfig
    self.engine = self.createEngineFromConfig(self.dbConfig)

  def createEngineFromConfig(self, dbConfig):
    return create_engine("%s://%s:%s@%s/%s" % (dbConfig.databaseType, dbConfig.userName, dbConfig.password, dbConfig.hostname, dbConfig.databaseName))