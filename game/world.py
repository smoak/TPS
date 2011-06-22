import logging, random

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
          num2 = -1
          num3 = -1
          num4 = -1
          num5 = -1
          num6 = -1
          num7 = -1
          num8 = -1
          newTileType = tile.tileType
          if tile.isTileStone():
            newTileType = 1
          frameX = tile.frameX
          frameY = tile.frameY
          if newTileType in [3, 24, 61, 71, 73, 74]:
            self.plantCheck(x, y)
          else:
            if x -1 < 0:
              num = newTileType
              num4 = newTileType
              num6 = newTileType
            if x + 1 >= self.width:
              num3 = newTileType
              num5 = newTileType
              num8 = newTileType
            if y - 1 < 0:
              num = newTileType
              num2 = newTileType
              num3 = newTileType
            if y + 1 >= self.height:
              num6 = newTileType
              num7 = newTileType
              num8 = newTileType
            if x - 1 >= 0 and self.tiles[x - 1][y].isActive:
              num4 = self.tiles[x - 1][y].tileType
            if x + 1 < self.width and self.tiles[x + 1][y].isActive:
              num5 = self.tiles[x + 1][y].tileType
            if y - 1 >= 0 and self.tiles[x][y - 1].isActive:
              num2 = self.tiles[x][y - 1].tileType
            if y + 1 < self.height and self.tiles[x][y + 1].isActive:
              num7 = self.tiles[x][y + 1].tileType
            if x - 1 >= 0 and y - 1 >= 0 and self.tiles[x - 1][y - 1].isActive:
              num = self.tiles[x - 1][y - 1].tileType
            if x + 1 < self.width and y - 1 >= 0 and self.tiles[x + 1][ y - 1].isActive:
              num3 = self.tiles[x + 1][y - 1].tileType
            if x - 1 >= 0 and y + 1 < self.height and self.tiles[x - 1][y + 1].isActive:
              num6 = self.tiles[x - 1][y + 1].tileType
            if x + 1 < self.width and y + 1 < self.height and self.tiles[x + 1][y + 1].isActive:
              num8 = self.tiles[x + 1][y + 1].tileType
            if num4 >= 0 and num4 in game.tile.STONE_TILES:
              num4 = 1
            if num5 >= 0 and num5 in game.tile.STONE_TILES:
              num5 = 1
            if num2 >= 0 and num2 in game.tile.STONE_TILES:
              num2 = 1
            if num7 >= 0 and num7 in game.tile.STONE_TILES:
              num7 = 1
            if num >= 0 and num in game.tile.STONE_TILES:
              num = 1
            if num3 >= 0 and num3 in game.tile.STONE_TILES:
              num3 = 1
            if num6 >= 0 and num6 in game.tile.STONE_TILES:
              num6 = 1
            if num8 >= 0 and num8 in game.tile.STONE_TILES:
              num8 = 1
            if newTileType == 4:
              if num7 >= 0 and num7 in game.tile.STONE_TILES and not (num7 in game.tile.NO_ATTACH_TILES):
                self.tiles[x][y] = self.tiles[x][y].copy()
                self.tiles[x][y].frameX = 0
              else:
                if (num4 >= 0 and num4 in game.tile.SOLID_TILES and not (num4 in game.tile.NO_ATTACH_TILES)) or (num4 == 5 and num == 5 and num6 == 5):
                  self.tiles[x][y] = self.tiles[x][y].copy()
                  self.tiles[x][y].frameX = 22
                else:
                  if (num5 >= 0 and num5 in game.tile.SOLID_TILES and not (num5 in game.tile.NO_ATTACH_TILES)) or (num5 == 5 and num3 == 5 and num8 == 5):
                    self.tiles[x][y] = self.tiles[x][y].copy()
                    self.tiles[x][y].frameX = 44
                  else:
                    self.killTile((x, y), False, False, False)
            else:
              if newTileType in [12, 31]:
                if not self.destroyObject:
                  num10 = x
                  num11 = y
                  if self.tiles[x][y].frameX != 0:
                    num10 = x - 1
                  if self.tiles[x][y].frameY != 0:
                    num11 = y - 1
                  if not self.tiles[num10][num11].isActive or self.tiles[num10][num11].tileType != newTileType or not self.tiles[num10 + 1][num11].isActive or self.tiles[num10 + 1][num11].tileType != newTileType or not self.tiles[num10][num11 + 1].isActive or self.tiles[num10][num11 + 1].tileType != newTileType or not self.tiles[num10 + 1][num11 + 1].isActive or self.tiles[num10 + 1][num11 + 1].tileType != newTileType:
                    self.destroyObject = True
                    if self.tiles[num10][num11].tileType == newTileType:
                      self.killTile((num10, num11), False, False, False)
                    if self.tiles[num10 + 1][num11].tileType == newTileType:
                      self.killTile((num10 + 1, num11), False, False, False)
                    if self.tiles[num10][num11 + 1].tileType == newTileType:
                      self.killTile((num10, num11 + 1), False, False, False)
                    if self.tiles[num10 + 1][num11 + 1].tileType == newTileType:
                      self.killTile((num10 + 1, num11 + 1), False, False, False)
                    if newTileType == 12:
                      print "Need to create a new item..."
                    else:
                      if newTileType == 31:
                        if random.randint(0, 2) == 0:
                          self.spawnMeteor = True
                        
                    
              

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
        if y + 1 < self.height and self.tiles[x][y + 1].isActive and ((self.tiles[x][y + 1].tileType == 2 and tileType == 3) or (self.tiles[x][y + 1].tileType == 23 and tileType == 24) or (self.tiles[x][y + 1].tileType == 78 and tileType == 3)):
          if tileType == 24 and random.randint(0, 13) == 0:
            tile.isActive = True
            tile.tileType = 32
            self.squareTileFrame((x, y), True)
          else:
            if self.tiles[x][y].tileType == 78:
              tile.isActive = True
              tile.tileType = tileType
              tile.frameX = random.randint(0, 2) * 18 + 108
            else:
              if self.tiles[x][y].wall == 0:
                if self.tiles[x][y + 1].wall == 0:
                  if random.randint(0, 50) == 0:
                    tile.isActive = True
                    tile.tileType = tileType
                    tile.frameX = 144
                  else:
                    if random.randint(0, 35) == 0:
                      tile.isActive = True
                      tile.tileType = tileType
                      tile.frameX = random.randint(0, 2) * 18 + 108
                    else:
                      tile.isActive = True
                      tile.tileType = tileType
                      tile.frameX = random.randint(0, 6) * 18
      elif tileType == 61:
        if y + 1 < self.height and self.tiles[x][y + 1].isActive and self.tiles[x][y + 1].tileType == 60:
          if random.randint(0,10) == 0 and y > self.dirtLayer:
            tile.isActive = True
            tile.tileType = 69
            self.squareTileFrame((x,y), True)
          else:
            if random.randint(0, 15) == 0 and y > self.dirtLayer:
              tile.isActive = True
              tile.tileType = tileType
              tile.frameX = 144
            else:
              if random.randint(0, 1000) == 0 and y > self.dirtLayer:
                tile.isActive = True
                tile.tileType = tileType
                tile.frameX = 162
              else:
                tile.isActive = True
                tile.tileType = tileType
                if y > self.dirtLayer:
                  tile.frameX = random.randint(0, 8) * 18
                else:
                  tile.frameX = random.randint(0, 6) * 18
      elif tileType == 71:
        if y + 1 < self.height and self.tiles[x][y + 1].isActive and self.tiles[x][y + 1].tileType == 70:
          tile.isActive = True
          tile.tileType = tileType
          tile.frameX = random.randint(0, 5) * 18
      elif tileType == 4:
        if (self.tiles[x - 1][y].isActive and (self.tiles[x - 1][y].isTileSolid() or (self.tiles[x - 1][y].tileType == 5 and self.tiles[x - 1][y - 1].tileType == 5 and self.tiles[x - 1][y + 1].tileType == 5))) or (self.tiles[x + 1][y].isActive and (self.tiles[x + 1][y].isTileSolid() or (self.tiles[x + 1][y].tileType == 5 and self.tiles[x + 1][y - 1].tileType == 5 and self.tiles[x + 1][y + 1].tileType == 5))) or (self.tiles[x][y + 1].isActive and self.tiles[x][y + 1].isTileSolid()):
          tile.isActive = True
          tile.tileType = tileType
          self.squareTileFrame((x, y), True)
      elif tileType == 10:
        pass
      elif tileType in [34, 35, 36]:
        self.place3x3(x, y, tileType)
        self.squareTileFrame((x, y), True)
      else:
        tile.isActive = True
        tile.tileType = tileType
    self.tiles[x][y] = tile
    
  def place3x3(self, x, y, tileType):
    flag = True
    for i in range(x - 1, x + 2):
      for j in range(y, y + 3):
        if self.tiles[i][j].isActive:
          flag = False
          break
    if not self.tiles[x][y - 1].isActive or not self.tiles[x][y - 1].isTileSolid() or self.tiles[x][y - 1].isTileSolidTop():
      flag = False
    if flag:
      self.tiles[x - 1][y] = self.tiles[x - 1][y].copy()
      self.tiles[x - 1][y].isActive = True
      self.tiles[x - 1][y].frameY = 0
      self.tiles[x - 1][y].frameX = 0
      self.tiles[x - 1][y].tileType = tileType
      
      self.tiles[x][y] = self.tiles[x][y].copy()
      self.tiles[x][y].isActive = True
      self.tiles[x][y].frameY = 0
      self.tiles[x][y].frameX = 18
      self.tiles[x][y].tileType = tileType
      
      self.tiles[x + 1][y] = self.tiles[x + 1][y].copy()
      self.tiles[x + 1][y].isActive = True
      self.tiles[x + 1][y].frameY = 0
      self.tiles[x + 1][y].frameX = 36
      self.tiles[x + 1][y].tileType = tileType
      
      self.tiles[x - 1][y + 1] = self.tiles[x - 1][y + 1].copy()
      self.tiles[x - 1][y + 1].isActive = True
      self.tiles[x - 1][y + 1].frameY = 18
      self.tiles[x - 1][y + 1].frameX = 0
      self.tiles[x - 1][y + 1].tileType = tileType
      
      self.tiles[x][y + 1] = self.tiles[x][y + 1].copy()
      self.tiles[x][y + 1].isActive = True
      self.tiles[x][y + 1].frameY = 18
      self.tiles[x][y + 1].frameX = 18
      self.tiles[x][y + 1].tileType = tileType
        
      self.tiles[x + 1][y + 1] = self.tiles[x + 1][y + 1].copy()
      self.tiles[x + 1][y + 1].isActive = True
      self.tiles[x + 1][y + 1].frameY = 18
      self.tiles[x + 1][y + 1].frameX = 36
      self.tiles[x + 1][y + 1].tileType = tileType

      self.tiles[x - 1][y + 2] =  self.tiles[x - 1][y + 2].copy()
      self.tiles[x - 1][y + 2].isActive = True
      self.tiles[x - 1][y + 2].frameY = 36
      self.tiles[x - 1][y + 2].frameX = 0
      self.tiles[x - 1][y + 2].tileType = tileType
       
      self.tiles[x][y + 2] = self.tiles[x][y + 2].copy()  
      self.tiles[x][y + 2].isActive = True
      self.tiles[x][y + 2].frameY = 36
      self.tiles[x][y + 2].frameX = 18
      self.tiles[x][y + 2].tileType = tileType
	
      self.tiles[x + 1][y + 2] = self.tiles[x + 1][y + 2].copy()
      self.tiles[x + 1][y + 2].isActive = True
      self.tiles[x + 1][y + 2].frameY = 36
      self.tiles[x + 1][y + 2].frameX = 36
      self.tiles[x + 1][y + 2].tileType = tileType
			
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
