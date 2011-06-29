from service.projectile import ProjectileService

class ProjectileFactory(object):
  def __init__(self, world):
    self.world = world
    self.projectileService = ProjectileService()
    # May want to break this out in a Manager class?
    self.projectiles = []
	  
  def newProjectile(self, x, y, speedX, speedY, projectileType, damage, knockBack, owner = 255):
    p = self.projectileService.getProjectileByType(projectileType)
    posX = x - p.width * 0.5
    posY = y - p.height * 0.5
    p.position = (posX, posY)
    p.velocity = (speedX, speedY)
    p.damage = damage
    p.knockBack = knockBack
    p.owner = owner
    p.wet = self.__wetCollision(p.position, p.width, p.height)
    p.identity = self.__nextAvailableNum()
    self.projectiles.append(p)
    return p
    
  def __wetCollision(self, position, width, height):
    vector = (position[0] + (width / 2.), position[1] + (height / 2.0))
    num = 10
    num2 = height / 2
    if num > width:
      num = width
    if num2 > height:
      num2 = height
    vector = (vector[0] - (num / 2.0), vector[1] - (num2 / 2.0))
    num3 = int((position[0] / 16.0) - 1.0)
    num4 = int(((position[0] + width) / 16.0) + 2.0)
    num5 = int((position[1] / 16.0) - 1.0)
    num6 = int(((position[1] + height) / 16.0) + 2.0)
    if num3 < 0:
      num3 = 0
    if num4 > self.world.width:
      num4 = self.world.width
    if num5 < 0:
      num5 = 0
    if num6 > self.world.height:
      num6 = self.world.height
    for i in range(num3, num4):
      for j in range(num5, num6):
        if self.world.tiles[i][j].liquid > 0:
          vector2 = (i * 16, j * 16)
          num7 = 16
          num8 = (0 - self.world.tiles[i][j].liquid)
          num8 /= 32.0
          vector2[1] += num8 * 2.0
          num7 -= (num8 * 2.0)
          if vector[0] + num > vector2[0] and vector[0] < vector2[0] + 16.0 and vector[1] + num2 > vector2[1] and vector[1] < vector2[1] + num7:
            return True
    return False

  def __nextAvailableNum(self):
    result = len(self.projectiles) + 1
    if result >= 1000:
      result = 999
    return result 
    
