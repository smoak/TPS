from sqlalchemy.orm.query import Query

from db.entities import WorldEntity
from db.mappers import WorldMapper

class BaseRepository(object):
  """
  Base repository class for entity persistance
  """
  
  def __init__(self, databaseAdapter):
    self.databaseAdapter = databaseAdapter
    
  def _saveEntity(self, entity):
    """
    Persists an entity object
    """
    self.databaseAdapter.session.add(entity)
    self.databaseAdapter.session.flush()

class WorldRepository(BaseRepository):
  """
  Persistance layer for L{WorldEntity} objects
  """
  
  worldMapper = WorldMapper()
  
  def getWorld(self, world):
    """
    Retrieves a L{World}
    """
    q = self.databaseAdapter.session.query(WorldEntity)
    if world.worldId > 0:
      q = q.filter_by(id=world.worldId)
    if len(world.name) > 1:
      q = q.filter_by(name=world.name)
    entity = q.first()
    self.worldMapper.entityToDomain(entity, world)
  
  def saveWorld(self, world):
    """
    Persists a L{World} domain object.
    """
    entity = WorldEntity()
    self.worldMapper.domainToEntity(world, entity)
    BaseRepository._saveEntity(self, entity)