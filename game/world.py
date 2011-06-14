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
    self.width = 1024 # maxTilesX
    self.height = 1024 # maxTilesY
    self.dirtLayer = 40 # worldSurface
    self.rockLayer = 20
    self.worldId = 0
    self.tiles = {}
    self.leftWorld = 0
    self.rightWorld = 0
    self.topWorld = 0
    self.bottomWorld = 0
    self.spawn = []
    self.worldSurface = 0.0
    self.items = []
    self.npcs = []
    self.waterLine = 0
    self.lavaLine = 0

  def getSectionX(self, x):
    return x / 200

  def getSectionY(self, y):
    return y / 150
  
  def killTile(self, coord, fail = False, effectOnly = False, noItem = False):
    x, y = coord[0], coord[1]
    if x < 0 or y < 0 or x >= self.width or y >= self.height:
      return
    if self.tiles[x][y].isActive:
      pass
    # TODO: Finish this!
  
