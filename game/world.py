import logging

from game.tile import *
from util.math import *
import game.tile
from game.item import *
from util.item import ItemGenerator

log = logging.getLogger()

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
    self.itemGenerator = ItemGenerator()
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
    for i in range(200):
      self.items.append(Item("Empty", 1))
    self.npcs = []
    self.waterLine = 0
    self.lavaLine = 0

  def getSectionX(self, x):
    return x / 200

  def getSectionY(self, y):
    return y / 150
  
  def killTile(self, coord, fail = False, effectOnly = False, noItem = False):
    x, y = coord[0], coord[1]
    newItem = None
    if x < 0 or y < 0 or x >= self.width or y >= self.height:
      return None
    if self.tiles[x][y].isActive:
      if y >= 1 and self.tiles[x][y - 1].isActive and ((self.tiles[x][y - 1].tileType == 5 and self.tiles[x][y].tileType != 5) or (self.tiles[x][y - 1].tileType == 21 and self.tiles[x][y].tileType != 21) or (self.tiles[x][y - 1].tileType == 26 and self.tiles[x][y].tileType != 26) or (self.tiles[x][y - 1].tileType == 72 and self.tiles[x][y].tileType != 72) or (self.tiles[x][y - 1].tileType == 12 and self.tiles[x][y].tileType != 12)):
        if self.tiles[x][y - 1].tileType != 5:
          return None
        if (self.tiles[x][y - 1].frameX != 66 or self.tiles[x][y - 1].frameY < 0 or self.tiles[x][y - 1].frameY > 44) and (self.tiles[x][y - 1].frameX != 88 or self.tiles[x][y - 1].frameY < 66 or self.tiles[x][y - 1].frameY > 110) and self.tiles[x][y - 1].frameY < 198:
          return None
    if not effectOnly:
      tile = self.tiles[x][y]
      if tile.tileType in ([3,24]):
        if tile.frameX == 144:
          newItem = self.itemGenerator.generateItemFromKillingTile(tile, x, y)
      if fail:
        if tile.tileType in ([2,23]):
          self.tiles[x][y] = tile.copy()
          self.tiles[x][y].tileType = 0
        if tile.tileType == 60:
          self.tiles[x][y] = tile.copy()
          self.tiles[x][y].tileType = 59
        self.squareTileFrame(coord, True)
      else:
        if tile.tileType == 21:
          cx = x - tile.frameX / 18
          cy = y - tile.frameY / 18
          if not self.destroyChest(cx, cy):
            return
        if not noItem:
          newItem = self.itemGenerator.generateItemFromKillingTile(tile, x, y)
        self.tiles[x][y] = tile.copy()
        self.tiles[x][y].isActive = False
        self.tiles[x][y].frameX = -1
        self.tiles[x][y].frameY = -1
        self.tiles[x][y].tileType = 0
        if self.tiles[x][y].isTileSolid():
          self.tiles[x][y].isLighted = False
        self.squareTileFrame(coord, True)
    itemNum = -1
    if newItem:
      itemNum = self.getNextItemNum()
      self.items[itemNum] = newItem
    return (newItem, itemNum)

  def squareTileFrame(self, coord, resetFrame = True):
    x, y = coord[0], coord[1]
    self.tileFrame(x - 1, y - 1, False, False)
    self.tileFrame(x - 1, y, False, False)
    self.tileFrame(x - 1, y + 1, False, False)
    self.tileFrame(x, y - 1, False, False)
    self.tileFrame(x, y, resetFrame, False)
    self.tileFrame(x, y + 1, False, False)
    self.tileFrame(x + 1, y - 1, False, False)
    self.tileFrame(x + 1, y, False, False)
    self.tileFrame(x + 1, y + 1, False, False)

  def tileFrame(self, x, y, resetFrame = False, noBreak = False):
    if x >= 0 and y >= 0 and x < self.width and y < self.height:
      tile = self.tiles[x][y]
      if tile.liquid > 0:
        self.addWater(x, y)
      if tile.isActive:
        if not noBreak or not tile.isImportant():
          num = -1
          newTileType = tile.tileType
          if tile.isTileStone():
            newTileType = 1
          frameX = tile.frameX
          frameY = tile.frameY
          if newTileType in [3, 24, 61, 71, 73, 74]:
            self.plantCheck(x, y)
          else:
            pass

  def plantCheck(self, x, y):
    pass

  def addWater(self, x, y):
    pass

  def destroyChest(self, x, y):
    return True

  def emptyTile(x, y, ignoreTiles = False):
    tile = self.tiles[x][y]
    if tile.isActive and not ignoreTiles:
      return False
    return True
    
  def getNextItemNum(self):
    for i in range(len(self.items)):
      item = self.items[i]
      if not item.active:
        return i
    return 0

  def placeTile(self, x, y, tileType, mute = False, forced = False, plr = -1):
    if x < 0 or y < 0 or x > self.width or y > self.height:
      return
    tile = self.tiles[x][y].copy()
    if forced or self.emptyTile(x, y, False) or not tileType in game.tile.SOLID_TILES or (tileType == 23 and self.tiles[x][y].tileType == 0 and self.tiles[x][y].isActive) or (tileType == 2 and self.tiles[x][y].tileType == 0 and self.tiles[x][y].isActive) or (tileType == 60 and self.tiles[x][y].tileType == 59 and self.tiles[x][y].isActive) or (tileType == 70 and self.tiles[x][y].tileType == 59 and self.tiles[x][y].isActive):
      if (tile.tileType != 0 or not tile.isActive) and tileType in [2, 23]:
        return
      if (tile.tileType != 50 or not tile.isActive) and tileType == 60:
        return
      if tile.liquid > 0:
        if tileType in [3, 4, 20, 24, 27, 32, 51, 69, 72]:
          return
      tile.frameY = 0
      tile.frameX = 0
      if tileType in [3, 24]:
        pass
      elif tileType == 61:
        pass
      else:
        tile.isActive = True
        tile.tileType = tileType
    self.tiles[x][y] = tile

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
