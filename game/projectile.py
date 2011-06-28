class Projectile(object):
  def __init__(self, name):
    self.name = name
    self.projectileType = -1
    self.width = 0
    self.height = 0
    self.aiStyle = 0
    self.position = (0,0)
    self.velocity = (0,0)
    self.damage = 0
    self.knockBack = 0
    self.identity = 0
    self.wet = False
    self.owner = 0
    self.ai = []
    
  def __repr__(self):
    return "<Projectile('%s', Type=%d, %dx%d)>" % (self.name, self.projectileType, self.width, self.height)