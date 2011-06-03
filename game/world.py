class MoonPhase:
  One = 0
  Two = 1
  Three = 2
  Four = 3
  Five = 4
  Six = 5
  Seven = 6
  Eight = 7

class World:

  def __init__(self):
    self.time = 54001
    self.moonphase = MoonPhase.Four
    self.isBloodMoon = False
    self.isDay = True
    self.name = ""
    self.spawn = (0,0)
    self.width = 1024
    self.height = 1024
    self.dirtLayer = 40
    self.rockLayer = 20
    self.worldId = 0
    self.tiles = []

  def getSectionX(self, x):
    return x / 200

  def getSectionY(self, y):
    return y / 150

  
