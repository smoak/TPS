from repository.projectile import JsonProjectileRepository
from game.projectile import Projectile

class ProjectileService(object):
  def __init__(self):
    self.projectileRepository = JsonProjectileRepository()
    
  def getProjectileByType(self, projectileType):
    entity = self.projectileRepository.getProjectileByType(projectileType)
    result = None
    if entity:
      result = Projectile(entity['name'].encode('ascii', 'ignore'))
      self.__mapEntityToDomain(entity, result)
    return result
    
  def __mapEntityToDomain(self, entity, domain):
    domain.projectileType = entity['type']
    domain.width = entity['width']
    domain.height = entity['height']
    domain.aiStyle = entity['aistyle']
    domain.ai = entity['ai']