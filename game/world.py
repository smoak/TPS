from game.tile import *

AIR_TILE = AirTile()

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
      if y >= 1 and self.tiles[x][y - 1].isActive and ((self.tiles[x][y - 1].tileType == 5 and self.tiles[x][y].tileType != 5) or (self.tiles[x][y - 1].tileType == 21 and self.tiles[x][y].tileType != 21) or (self.tiles[x][y - 1].tileType == 26 and self.tiles[x][y].tileType != 26) or (self.tiles[x][y - 1].tileType == 72 and self.tiles[x][y].tileType != 72) or (self.tiles[x][y - 1].tileType == 12 and self.tiles[x][y].tileType != 12)):
        if self.tiles[x][y - 1].tileType != 5:
          return
        if (self.tiles[x][y - 1].frameX != 66 or self.tiles[x][y - 1].frameY < 0 or self.tiles[x][y - 1].frameY > 44) and (self.tiles[x][y - 1].frameX != 88 or self.tiles[x][y - 1].frameY < 66 or self.tiles[x][y - 1].frameY > 110) and self.tiles[x][y - 1].frameY < 198:
          return
    if not effectOnly:
      tile = self.tiles[x][y]
      if tile.tileType == 3:
        if tile.frameX == 144:
          newItemX = x * 16
          newItemY = y * 16
          newItemWidth = 16
          newItemHeight = 16
          newItemType = 5
          newItemStack = 1
    self.tiles[x][y] = AIR_TILE
    # TODO: Finish this!
  
  def update(self, elapsedMs):
    self.time += elapsedMs
    if not self.isDay:
      if self.time > 32400.0:
        self.time = 0.0
        self.isDay = True
        self.moonphase += 1
        if self.moonphase >= 8:
          self.moonphase = 0
    else:
      if self.time > 54000.0:
        self.time = 0.0
        self.isDay = False
