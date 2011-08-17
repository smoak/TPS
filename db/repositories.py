from sqlalchemy.orm.query import Query

from db.entities import WorldEntity
from db.mappers import WorldMapper

class BaseRepository(object):
  """
  Base repository class for entity persistance
  """
  
  def __init__(self, databaseAdapter):
    self.databaseAdapter = databaseAdapter
    
  def __saveEntity(self, entity):
    """
    Persists an entity object
    """
    self.databaseAdapter.saveEntity(entity)

class WorldRepository(BaseRepository):
  """
  Persistance layer for L{WorldEntity} objects
  """
  
  worldMapper = WorldMapper()
  
  def getWorld(self, world):
    """
    Retrieves a L{World}
    """
    q = Query(WorldEntity)
    if world.worldId > 0:
      q = q.filter_by(id=world.worldId)
    if len(world.name) > 1:
      q = q.filter_by(name=world.name
    entity = self.databaseAdapter.query(WorldEntity).from_statement(q.statement).first()
    self.worldMapper.entityToDomain(entity, domain)
  
  def saveWorld(self, world):
    """
    Persists a L{World} domain object.
    """
    entity = WorldEntity()
    self.worldMapper.domainToEntity(world, entity)
    self.__saveEntity(entity)