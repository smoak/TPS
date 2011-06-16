class Npc(object):
  def __init__(self):
    self.name = ""
    self.posX = 0
    self.posY = 0
    self.velX = 0
    self.velY = 0
    self.target = 0
    self.directionX = 0
    self.directionY = 0
    self.life = 0
    self.ai = []
    self.wet = False

  def doAi(self):
    pass

  def update(self):
    num = 10.0
    num2 = 0.3
    if self.wet:
      num2 = 0.2
      num = 7.0
    self.doAi()
