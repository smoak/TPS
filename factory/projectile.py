from service.projectile import ProjectileService

class ProjectileFactory(object):
  def __init__(self):
    self.projectileService = ProjectileService()
    # May want to break this out in a Manager class?
    self.projecties = []
	  
  def newProjectile(self, x, y, speedX, speedY, projectileType, damage, knockBack, owner = 255, wet = False):
    p = self.projectileService.getProjectileByType(projectileType)
    posX = x - p.width * 0.5
    posY = y - p.height * 0.5
    p.position = (posX, posY)
    p.velocity = (speedX, speedY)
    p.damage = damage
    p.knockBack = knockBack
    p.owner = owner
    p.wet = wet # Hmmm...this is really supposed to be some sort of weird collision detection thing..
    p.identity = self.__nextAvailableNum()
    self.projectiles.append(p)
    return p

  def __nextAvailableNum(self):
    result = len(self.projectiles) + 1
    if result >= 1000:
      result = 999
    return result 
    
