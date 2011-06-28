from service.projectile import ProjectileService

class ProjectileFactory(object):
  def __init__(self):
    self.projectileService = ProjectileService()
	  
  def newProjectile(self, x, y, speedX, speedY, projectileType, damage, knockBack, owner = 255, wet = False):
    p = self.projectileService.getProjectileByType(projectileType)
    posX = x - p.width * 0.5
    posY = y - p.height * 0.5
    p.position = (posX, posY)
    p.velocity = (speedX, speedY)
    p.damage = damage
    p.knockBack = knockBack
    p.owner = owner
    p.wet = wet
    