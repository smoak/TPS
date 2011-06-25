import logging, random

from game.tile import *
from util.math import *
from common.events import EventHook, ItemCreatedEventArgs
import game.tile
from game.item import *
from util.item import ItemGenerator
from game.chest import Chest

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

class World(object):

  def __init__(self):
    self.itemGenerator = ItemGenerator()
    self.time = 54001
    self.moonphase = MoonPhase.Four
    self.isBloodMoon = False
    self.isDay = True
    self.destroyObject = False
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
    self.chests = []
    self.npcs = []
    self.players = []
    self.waterLine = 0
    self.lavaLine = 0
    self.onItemCreated = EventHook()

  def getSectionX(self, x):
    return x / 200

  def getSectionY(self, y):
    return y / 150
  
  def killTile(self, coord, fail = False, effectOnly = False, noItem = False):
    x, y = coord[0], coord[1]
    newItem = None
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
      self.onItemCreated.fire(eventArgs=ItemCreatedEventArgs(newItem, itemNum))

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
          tmpFrameX = -1
          tmpFrameY = -1
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
                        num12 = random.randint(0, 5)
                        if not self.shadowOrbSmashed:
                          num12 = 0
                        if num12 == 0:
                          print "Need to create a new item...based on num12"
                        self.shadowOrbSmashed = True
                        self.shadowOrbCount += 1
                        if self.shadowOrbCount >= 3:
                          self.shadowOrbCount = 0
                          num12 = num10 * 16
                          num13 = num11 * 16
                          num15 = -1
                          plr = 0
                          print "need to spawn an npc on player"
                        else:
                          print "need to send the chill text to player"
              else:
                if newTileType == 19:
                  if num4 == newTileType and num5 == newTileType:
                    if self.tiles[x][y].frameNumber == 0:
                      tmpFrameX = 0
                      tmpFrameY = 0
                    if self.tiles[x][y].frameNumber == 1:
                      tmpFrameX = 0
                      tmpFrameY = 18
                    if self.tiles[x][y].frameNumber == 2:
                      tmpFrameX = 0
                      tmpFrameY = 36
                  elif num4 == newTileType and num5 == -1:
                    if self.tiles[x][y].frameNumber == 0:
                      tmpFrameX = 18
                      tmpFrameY = 0
                    if self.tiles[x][y].frameNumber == 1:
                      tmpFrameX = 36
                      tmpFrameY = 18
                    if self.tiles[x][y].frameNumber == 2:
                      tmpFrameX = 36
                      tmpFrameY = 36
                  elif num4 == -1 and num5 == newTileType:
                    if self.tiles[x][y].frameNumber == 0:
                      tmpFrameX = 36
                      tmpFrameY = 0
                    if self.tiles[x][y].frameNumber == 1:
                      tmpFrameX = 36
                      tmpFrameY = 18
                    if self.tiles[x][y].frameNumber == 2:
                      tmpFrameX = 36
                      tmpFrameY = 36
                  elif num4 != newTileType and num5 == newTileType:
                    if self.tiles[x][y].frameNumber == 0:
                      tmpFrameX = 54
                      tmpFrameY = 0
                    if self.tiles[x][y].frameNumber == 1:
                      tmpFrameX = 54
                      tmpFrameY = 18
                    if self.tiles[x][y].frameNumber == 2:
                      tmpFrameX = 54
                      tmpFrameY = 36
                  elif num4 == newTileType and num5 != newTileType:
                    if self.tiles[x][y].frameNumber == 0:
                      tmpFrameX = 72
                      tmpFrameY = 0
                    if self.tiles[x][y].frameNumber == 1:
                      tmpFrameX = 72
                      tmpFrameY = 18
                    if self.tiles[x][y].frameNumber == 2:
                      tmpFrameX = 72
                      tmpFrameY = 36
                  elif num4 != newTileType and num4 != -1 and num5 == -1:
                    if self.tiles[x][y].frameNumber == 0:
                      tmpFrameX = 108
                      tmpFrameY = 0
                    if self.tiles[x][y].frameNumber == 1:
                      tmpFrameX = 108
                      tmpFrameY = 18
                    if self.tiles[x][y].frameNumber == 2:
                      tmpFrameX = 108
                      tmpFrameY = 36
                  elif num4 == -1 and num5 != newTileType and num5 != -1:
                    if self.tiles[x][y].frameNumber == 0:
                      tmpFrameX = 126
                      tmpFrameY = 0
                    if self.tiles[x][y].frameNumber == 1:
                      tmpFrameX = 126
                      tmpFrameY = 18
                    if self.tiles[x][y].frameNumber == 2:
                      tmpFrameX = 126
                      tmpFrameY = 36
                  else:
                    if self.tiles[x][y].frameNumber == 0:
                      tmpFrameX = 90
                      tmpFrameY = 0
                    if self.tiles[x][y].frameNumber == 1:
                      tmpFrameX = 90
                      tmpFrameY = 18
                    if self.tiles[x][y].frameNumber == 2:
                      tmpFrameX = 90
                      tmpFrameY = 36
                else:
                  if newTileType == 10:
                    if not self.destroyObject:
                      frameY2 = self.tiles[x][y].frameY
                      num11 = y
                      flag = False
                      if frameY2 == 18:
                        num11 = y - 1
                      if frameY2 == 36:
                        num11 = y - 2
                      if not self.tiles[x][num11 - 1].isActive or not self.tiles[x][num11 - 1].isTileSolid() or not self.tiles[x][num11 + 3].isActive or not self.tiles[x][num11 + 3].isTileSolid() or not self.tiles[x][num11].isActive or self.tiles[x][num11].tileType != newTileType or not self.tiles[x][num11 + 1].isActive or self.tiles[x][num11 + 1].tileType != newTileType or not self.tiles[x][num11 + 2].isActive or self.tiles[x][num11 + 2].tileType != newTileType:
                        flag = True
                      if flag:
                        self.destroyObject = True
                        self.killTile((x, num11), False, False, False)
                        self.killTile((x, num11 + 1), False, False, False)
                        self.killTile((x, num11 + 2), False, False, False)
                        print "tileFrame Should generate new item"
                      self.destroyObject = False
                    return
                  if newTileType == 11:
                    if not self.destroyObject:
                      num17 = 0
                      num10 = x
                      num11 = y
                      frameX2 = self.tiles[x][y].frameX
                      frameY2 = self.tiles[x][y].frameY
                      flag = False
                      if frameX2 == 0:
                        num17 = 1
                      elif frameX2 == 18:
                        num10 = x - 1
                        num17 = 1
                      elif frameX2 == 36:
                        num10 = x + 1
                        num17 = -1
                      elif frameX2 == 54:
                        num10 = x
                        num17 = -1
                      if frameY2 == 18:
                        num11 = y - 1
                      elif frameY2 == 36:
                        num11 = y - 2
                      if not self.tiles[num10][num11 - 1].isActive or not self.tiles[num10][num11 - 1].isTileSolid() or self.tiles[num10][num11 + 3].isActive or self.tiles[num10][num11 + 3].isTileSolid():
                        flag = True
                        self.destroyObject = True
                        print "new item..."
                      num18 = num10
                      if num17 == -1:
                        num18 = num10 - 1
                      for l in range(num18, num18 + 2):
                        for m in range(num11, num11 + 3):
                          if not flag:
                            if self.tiles[l][m].tileType != 11 or not self.tiles[l][m].isActive:
                              self.destroyObject = True
                              print "New item..."
                              flag = True
                              l = num18
                              m = num11
                          if flag:
                            self.killTile((l, m), False, False, False)
                      self.destroyObject = False
                    return
                  if newTileType in [34, 35, 36]:
                    self.check3x3(x, y, newTileType)
                    return
                  if newTileType in [15, 20]:
                    self.check1x2(x, y, newTileType)
                    return
                  if newTileType in [14, 17, 26, 77]:
                    self.check3x2(x, y, newTileType)
                    return
                  if newTileType in [16, 18, 29]:
                    self.check2x1(x, y, newTileType)
                    return
                  if newTileType in [13, 33, 49, 50, 78]:
                    self.checkOnTable1x1(x, y, newTileType)
                    return
                  if newTileType == 21:
                    self.checkChest(x, y, newTileType)
                    return
                  if newTileType == 27:
                    self.checkSunflower(x, y, 27)
                    return
                  if newTileType == 28:
                    self.checkPot(x, y, 28)
                    return
                  if newTileType == 42:
                    self.check1x2Top(x, y, newTileType)
                    return
                  if newTileType == 55:
                    self.checkSign(x, y, newTileType)
                    return
                  if newTileType == 79:
                    self.check4x2(x, y, newTileType)
                    return
                if newTileType == 72:
                  if num7 != newTileType and num7 != 70:
                    self.killTile(x, y, False, False, False)
                  else:
                    if num2 != newTileType and self.tiles[x][y].frameX == 0:
                      self.tiles[x][y] = self.tiles[x][y].copy()
                      self.tiles[x][y].frameNumber = random.randint(0, 3)
                      if self.tiles[x][y].frameNumber == 0:
                        self.tiles[x][y].frameX = 18
                        self.tiles[x][y].frameY = 0
                      if self.tiles[x][y].frameNumber == 1:
                        self.tiles[x][y].frameX = 18
                        self.tiles[x][y].frameY = 18
                      if self.tiles[x][y].frameNumber == 2:
                        self.tiles[x][y] = 18
                        self.tiles[x][y] = 36
                if newTileType == 5:
                  if num7 == 23:
                    num7 = 2
                  if num7 == 60:
                    num7 = 2
                  if self.tiles[x][y].frameX >= 22 and self.tiles[x][y].frameX <= 44 and self.tiles[x][y].frameY >= 132 and self.tiles[x][y].frameY <= 176:
                    if ((num4 != newTileType and num5 != newTileType) or num7 != 2):
                      self.killTile((x, y), False, False, False)
                  else:
                    if ((self.tiles[x][y].frameX == 88 and self.tiles[x][y].frameY >= 0 and self.tiles[x][y].frameY <= 44) or (self.tiles[x][y].frameX == 66 and self.tiles[x][y].frameY >= 66 and self.tiles[x][y].frameY <= 130) or (self.tiles[x][y].frameX == 110 and self.tiles[x][y].frameY >= 66 and self.tiles[x][y].frameY <= 110) or (self.tiles[x][y].frameX == 132 and self.tiles[x][y].frameY >= 0 and self.tiles[x][y].frameY <= 176)):
                      if num4 == newTileType and num5 == newTileType:
                        self.tiles[x][y] = self.tiles[x][y].copy()
                        if self.tiles[x][y].frameNumber == 0:
                          self.tiles[x][y].frameX = 110
                          self.tiles[x][y].frameY = 66
                        if self.tiles[x][y].frameNumber == 1:
                          self.tiles[x][y].frameX = 110
                          self.tiles[x][y].frameY = 88
                        if self.tiles[x][y].frameNumber == 2:
                          self.tiles[x][y].frameX = 110
                          self.tiles[x][y].frameY = 110
                      elif num4 == newTileType:
                        self.tiles[x][y] = self.tiles[x][y].copy()
                        if self.tiles[x][y].frameNumber == 0:
                          self.tiles[x][y].frameX = 88
                          self.tiles[x][y].frameY = 0
                        if self.tiles[x][y].frameNumber == 1:
                          self.tiles[x][y].frameX = 88
                          self.tiles[x][y].frameY = 22
                        if self.tiles[x][y].frameNumber == 2:
                          self.tiles[x][y].frameX = 88
                          self.tiles[x][y].frameY = 44
                      elif num5 == newTileType:
                        self.tiles[x][y] = self.tiles[x][y].copy()
                        if self.tiles[x][y].frameNumber == 0:
                          self.tiles[x][y].frameX = 66
                          self.tiles[x][y].frameY = 66
                        if self.tiles[x][y].frameNumber == 1:
                          self.tiles[x][y].frameX = 66
                          self.tiles[x][y].frameY = 88
                        if self.tiles[x][y].frameNumber == 2:
                          self.tiles[x][y].frameX = 66
                          self.tiles[x][y].frameY = 110
                      else:
                        self.tiles[x][y] = self.tiles[x][y].copy()
                        if self.tiles[x][y].frameNumber == 0:
                          self.tiles[x][y].frameX = 0
                          self.tiles[x][y].frameY = 0
                        if self.tiles[x][y].frameNumber == 1:
                          self.tiles[x][y].frameX = 0
                          self.tiles[x][y].frameY = 22
                        if self.tiles[x][y].frameNumber == 2:
                          self.tiles[x][y].frameX = 0
                          self.tiles[x][y].frameY = 44
                  if self.tiles[x][y].frameY >= 132 and self.tiles[x][y].frameY <= 176:
                    pass
              

  def plantCheck(self, x, y):
    pass

  def addWater(self, x, y):
    pass

  def destroyChest(self, x, y):
    chest = None
    
    # Find the chest entry with x and y coordinate
    for c in self.chests:
      if c.x == x and c.y == y:
        chest = c
        break
        
    if chest:
      if chest.hasItems():
        return False
      # no items in the chest so remove it
      self.chests.remove(chest)
        
    return True

  def emptyTile(x, y, ignoreTiles = False):
    tile = self.tiles[x][y]
    if tile.isActive and not ignoreTiles:
      return False
    else:
      for p in self.players:
        if p.active:
          pass
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
            self.tiles[x][y] = tile
            self.squareTileFrame((x, y), True)
          else:
            if self.tiles[x][y].tileType == 78:
              tile.isActive = True
              tile.tileType = tileType
              tile.frameX = random.randint(0, 2) * 18 + 108
              self.tiles[x][y] = tile
            else:
              if self.tiles[x][y].wall == 0:
                if self.tiles[x][y + 1].wall == 0:
                  if random.randint(0, 50) == 0:
                    tile.isActive = True
                    tile.tileType = tileType
                    tile.frameX = 144
                    self.tiles[x][y] = tile
                  else:
                    if random.randint(0, 35) == 0:
                      tile.isActive = True
                      tile.tileType = tileType
                      tile.frameX = random.randint(0, 2) * 18 + 108
                    else:
                      tile.isActive = True
                      tile.tileType = tileType
                      tile.frameX = random.randint(0, 6) * 18
                    self.tiles[x][y] = tile
      elif tileType == 61:
        if y + 1 < self.height and self.tiles[x][y + 1].isActive and self.tiles[x][y + 1].tileType == 60:
          if random.randint(0,10) == 0 and y > self.dirtLayer:
            tile.isActive = True
            tile.tileType = 69
            self.tiles[x][y] = tile
            self.squareTileFrame((x,y), True)
          else:
            if random.randint(0, 15) == 0 and y > self.dirtLayer:
              tile.isActive = True
              tile.tileType = tileType
              tile.frameX = 144
              self.tiles[x][y] = tile
            else:
              if random.randint(0, 1000) == 0 and y > self.dirtLayer:
                tile.isActive = True
                tile.tileType = tileType
                tile.frameX = 162
                self.tiles[x][y] = tile
              else:
                tile.isActive = True
                tile.tileType = tileType
                if y > self.dirtLayer:
                  tile.frameX = random.randint(0, 8) * 18
                else:
                  tile.frameX = random.randint(0, 6) * 18
                self.tiles[x][y] = tile
      elif tileType == 71:
        if y + 1 < self.height and self.tiles[x][y + 1].isActive and self.tiles[x][y + 1].tileType == 70:
          tile.isActive = True
          tile.tileType = tileType
          tile.frameX = random.randint(0, 5) * 18
          self.tiles[x][y] = tile
      elif tileType == 4:
        if (self.tiles[x - 1][y].isActive and (self.tiles[x - 1][y].isTileSolid() or (self.tiles[x - 1][y].tileType == 5 and self.tiles[x - 1][y - 1].tileType == 5 and self.tiles[x - 1][y + 1].tileType == 5))) or (self.tiles[x + 1][y].isActive and (self.tiles[x + 1][y].isTileSolid() or (self.tiles[x + 1][y].tileType == 5 and self.tiles[x + 1][y - 1].tileType == 5 and self.tiles[x + 1][y + 1].tileType == 5))) or (self.tiles[x][y + 1].isActive and self.tiles[x][y + 1].isTileSolid()):
          tile.isActive = True
          tile.tileType = tileType
          self.tiles[x][y] = tile
          self.squareTileFrame((x, y), True)
      elif tileType == 10:
        if not self.tiles[x][y - 1].isActive and not self.tiles[x][y - 2].isActive and self.tiles[x][y - 3].isActive and self.tiles[x][y - 3].isTileSolid():
          self.placeDoor(x, y - 1, tileType)
          self.squareTileFrame((x, y), True)
        else:
          if self.tiles[x][y + 1].isActive or self.tiles[x][y + 2].isActive or not self.tiles[x][y + 3].isActive or self.tiles[x][y + 3].isTileSolid():
            return
          self.placeDoor(x, y + 1, tileType)
          self.squareTileFrame((x, y), True)
      elif tileType in [34, 35, 36]:
        self.place3x3(x, y, tileType)
        self.squareTileFrame((x, y), True)
      elif tileType in [13, 33, 49, 50, 78]:
        self.placeOnTable1x1(x, y, tileType)
        self.squareTileFrame((x, y), True)
      elif tileType in [14, 26]:
        self.place3x2(x, y, tileType)
        self.squareTileFrame((x, y), True)
      elif tileType == 20:
        if self.tiles[x][y + 1].isActive and self.tiles[x][y + 1].tileType == 2:
          self.place1x2(x, y, tileType)
          self.squareTileFrame((x, y), True)
      elif tileType == 15:
        self.place1x2(x, y, tileType)
        self.squareTileFrame((x,y), True)
      elif tileType in [16, 18, 29]:
        self.place2x1(x, y, tileType)
        self.squareTileFrame((x, y), True)
      elif tileType in [17, 77]:
        self.place3x2(x, y, tileType)
        self.squareTileFrame((x, y), True)
      elif tileType == 21:
        self.placeChest(x, y, tileType)
        self.squareTileFrame((x, y), True)
      elif tileType == 27:
        self.placeSunflower(x, y, 27)
        self.squareTileFrame((x, y), True)
      elif tileType == 28:
        self.placePot(x, y, 28)
        self.squareTileFrame((x, y), True)
      elif tileType == 42:
        self.place1x2Top(x, y, tileType)
        self.squareTileFrame((x, y), True)
      elif tileType == 55:
        self.placeSign(x, y, tileType)
      elif tileType == 79:
        direction = 1
        if plr > -1:
          direction = self.players[plr].direction
        self.place4x2(x, y, tileType, direction)
      else:
        tile.isActive = True
        tile.tileType = tileType
        self.tiles[x][y] = tile
        
  def createChest(self, x, y):
    for c in self.chests:
      if c.x == x and c.y == y:
        return -1
    if len(self.chests) < 1000:
      c = Chest()
      c.x = x
      c.y = y
      self.chests.append(c)
      # return new index of the chest
      return len(self.chests) - 1
    
    return -1
    
  def place1x2(self, x, y, tileType):
    frameX = 0
    if tileType == 20:
      frameX = random.randint(0, 3) * 18
    if self.tiles[x][y + 1].isActive and self.tiles[x][y + 1].isTileSolid() and not self.tiles[x][y - 1].isActive:
      self.tiles[x][y - 1] = self.tiles[x][y - 1].copy()
      self.tiles[x][y - 1].isActive = True
      self.tiles[x][y - 1].frameY = 0
      self.tiles[x][y - 1].frameX = frameX
      self.tiles[x][y - 1].tileType = tileType
      
      self.tiles[x][y] = self.tiles[x][y].copy()
      self.tiles[x][y].frameY = 18
      self.tiles[x][y].frameX = frameX
      self.tiles[x][y].tileType = tileType
			
  def place2x1(self, x, y, tileType):
    flag = False
    if tileType != 29 and self.tiles[x][y + 1].isActive and self.tiles[x + 1][y + 1].isActive and self.tiles[x][y + 1].isTileSolid() and self.tiles[x + 1][y + 1].isTileSolid() and not self.tiles[x][y].isActive and not self.tiles[x + 1][y].isActive:
      flag = True
    else:
      if tileType == 29 and self.tiles[x][y + 1].isActive and self.tiles[x + 1][y + 1].isActive and self.tiles[x][y + 1].isTileTable() and self.tiles[x + 1][y + 1].isTileTabale() and not self.tiles[x][y].isActive and not self.tiles[x + 1][y].isActive:
        flag = True
    if flag:
      self.tiles[x][y] = self.tiles[x][y].copy()
      self.tiles[x][y].isActive = True
      self.tiles[x][y].frameY = 0
      self.tiles[x][y].frameX = 0
      self.tiles[x][y].tileType = tileType
      
      self.tiles[x + 1][y] = self.tiles[x + 1][y].copy()
      self.tiles[x + 1][y].isActive = True
      self.tiles[x + 1][y].frameY = 0
      self.tiles[x + 1][y].frameX = 18
      self.tiles[x + 1][y].tileType = tileType
    
  def place3x2(self, x, y, tileType):
    if x >= 5 and x < self.width - 5 and y >= 5 and y <= self.height - 5:
      flag = True
      for i in range(x - 1, x + 2):
        for j in range(y - 1, y + 1):
          if self.tiles[i][j].isActive:
            flag = False
            break
        if not self.tiles[i][y + 1].isActive or not self.tiles[i][y + 1].isTileSolid():
          flag = False
          break
      if flag:
        self.tiles[x - 1][y - 1] = self.tiles[x - 1][y - 1].copy()
        self.tiles[x - 1][y - 1].frameY = 0
        self.tiles[x - 1][y - 1].frameX = 0
        self.tiles[x - 1][y - 1].tileType = tileType
        
        self.tiles[x][y - 1] = self.tiles[x][y - 1].copy()
        self.tiles[x][y - 1].isActive = True
        self.tiles[x][y - 1].frameY = 0
        self.tiles[x][y - 1].frameX = 18
        self.tiles[x][y - 1].tileType = tileType
        
        self.tiles[x + 1][y - 1] = self.tiles[x + 1][y - 1].copy()
        self.tiles[x + 1][y - 1].isActive = True
        self.tiles[x + 1][y - 1].frameY = 0
        self.tiles[x + 1][y - 1].frameX = 36
        self.tiles[x + 1][y - 1].tileType = tileType
        
        self.tiles[x - 1][y] = self.tiles[x - 1][y].copy()
        self.tiles[x - 1][y].isActive = True
        self.tiles[x - 1][y].frameY = 18
        self.tiles[x - 1][y].frameX = 0
        self.tiles[x - 1][y].tileType = tileType
        
        self.tiles[x][y] = self.tiles[x][y].copy()
        self.tiles[x][y].isActive = True
        self.tiles[x][y].frameY = 18
        self.tiles[x][y].frameX = 18
        self.tiles[x][y].tileType = tileType
        
        self.tiles[x + 1][y] = self.tiles[x + 1][y].copy()
        self.tiles[x + 1][y].isActive = True
        self.tiles[x + 1][y].frameY = 18
        self.tiles[x + 1][y].frameX = 36
        self.tiles[x + 1][y].tileType = tileType
    
  def placeChest(self, x, y, tileType):
    flag = True
    num = -1
    for i in range(x, x + 2):
      for j in range(y - 1, y + 1):
        if self.tiles[i][j].isActive:
          flag = False
          break
        if self.tiles[i][j].isLava:
          flag = False
          break
      if not self.tiles[i][y + 1].isActive or not self.tiles[i][y + 1].isTileSolid():
        flag = False
        break
    if flag:
      num = self.createChest(x, y - 1)
      if num == -1:
        flag = False
    if flag:
      self.tiles[x][y - 1] = self.tiles[x][y - 1].copy()
      self.tiles[x][y - 1].isActive = True
      self.tiles[x][y - 1].frameY = 0
      self.tiles[x][y - 1].frameX = 0
      self.tiles[x][y - 1].tileType = tileType
      
      self.tiles[x + 1][y - 1] = self.tiles[x + 1][y - 1].copy()
      self.tiles[x + 1][y - 1].isActive = True
      self.tiles[x + 1][y - 1].frameY = 0
      self.tiles[x + 1][y - 1].frameX = 18
      self.tiles[x + 1][y - 1].tileType = tileType
      
      self.tiles[x][y] = self.tiles[x][y].copy()
      self.tiles[x][y].isActive = True
      self.tiles[x][y].frameY = 18
      self.tiles[x][y].frameX = 0
      self.tiles[x][y].tileType = tileType
      
      self.tiles[x + 1][y] = self.tiles[x + 1][y].copy()
      self.tiles[x + 1][y].isActive = True
      self.tiles[x + 1][y].frameY = 18
      self.tiles[x + 1][y].frameX = 18
      self.tiles[x + 1][y].tileType = tileType
    
  def placeSunflower(self, x, y, tileType = 27):
    if y <= self.dirtLayer - 1.0:
      flag = True
      for i in range(x, x + 2):
        for j in range(y - 3, y + 1):
          if self.tiles[i][j].isActive or self.tiles[i][j].wall > 0:
            flag = False
            break
        if not self.tiles[i][y + 1].isActive or self.tiles[i][y + 1].tileType != 2:
          flag = False
          break
      if flag:
        for i in range(2):
          for j in range(-3, 1):
            frameX = i * 18 + random.randint(0, 3) * 36
            frameY = (j + 3) * 18
            self.tiles[x + i][y + j] = self.tiles[x + i][y + j].copy()
            self.tiles[x + i][y + j].isActive = True
            self.tiles[x + i][y + j].frameX = frameX
            self.tiles[x + i][y + j].frameY = frameY
            self.tiles[x + i][y + j].tileType = tileType
    
  def place4x2(self, x, y, tileType, direction = -1):
    if x >= 5 and x <= self.width - 5 and y >= 5 and y <= self.height - 5:
      flag = True
      for i in range(x - 1, x + 3):
        for j in range(y - 1, y + 1):
          if self.tiles[i][j].isActive:
            flag = False
            break
        if not self.tiles[i][y + 1].isActive or not self.tiles[i][y + 1].isTileSolid():
          flag = False
          break
      frameX = 0
      if direction == 1:
        frameX = 72
      if flag:
        self.tiles[x - 1][y - 1] = self.tiles[x - 1][y - 1].copy()
        self.tiles[x - 1][y - 1].isActive = True
        self.tiles[x - 1][y - 1].frameY = 0
        self.tiles[x - 1][y - 1].frameX = frameX
        self.tiles[x - 1][y - 1].tileType = tileType
        
        self.tiles[x][y - 1] = self.tiles[x][y - 1].copy()
        self.tiles[x][y - 1].isActive = True
        self.tiles[x][y - 1].frameY = 0
        self.tiles[x][y - 1].frameX = 18 + frameX
        self.tiles[x][y - 1].tileType = tileType
        
        self.tiles[x + 1][y - 1] = self.tiles[x + 1][y - 1].copy()
        self.tiles[x + 1][y - 1].isActive = True
        self.tiles[x + 1][y - 1].frameY = 0
        self.tiles[x + 1][y - 1].frameX = 36 + frameX
        self.tiles[x + 1][y - 1].tileType = tileType
        
        self.tiles[x + 2][y - 1] = self.tiles[x + 2][y - 1].copy()
        self.tiles[x + 2][y - 1].isActive = True
        self.tiles[x + 2][y - 1].frameY = 0
        self.tiles[x + 2][y - 1].frameX = 54 + frameX
        self.tiles[x + 2][y - 1].tileType = tileType
        
        self.tiles[x - 1][y] = self.tiles[x - 1][y].copy()
        self.tiles[x - 1][y].isActive = True
        self.tiles[x - 1][y].frameY = 18
        self.tiles[x - 1][y].frameX = frameX
        self.tiles[x - 1][y].tileType = tileType
        
        self.tiles[x][y] = self.tiles[x][y].copy()
        self.tiles[x][y].isActive = True
        self.tiles[x][y].frameY = 18
        self.tiles[x][y].frameX = 18 + frameX
        self.tiles[x][y].tileType = tileType
        
        self.tiles[x + 1][y] = self.tiles[x + 1][y].copy()
        self.tiles[x + 1][y].isActive = True
        self.tiles[x + 1][y].frameY = 18
        self.tiles[x + 1][y].frameX = 36 + frameX
        self.tiles[x + 1][y].tileType = tileType
        
        self.tiles[x + 2][y] = self.tiles[x + 2][y].copy()
        self.tiles[x + 2][y].isActive = True
        self.tiles[x + 2][y].frameY = 18
        self.tiles[x + 2][y].frameX = 54 + frameX
        self.tiles[x + 2][y].tileType = tileType
    
  def rangeFrame(self, startX, startY, endX, endY):
    num = endX + 1
    num2 = endY + 1
    for i in range(startX - 1, num + 1):
      for j in range(startY - 1, num2 + 1):
        self.tileFrame(i, j, False, False)
    
  def placeSign(self, x, y, tileType):
    num = x - 2
    num2 = x + 3
    num3 = y - 2
    num4 = y + 3
    if num < 0 or num2 > self.width or num3 < 0 or num4 > self.height:
      return
    num5 = x
    num6 = y
    num7 = 0
    if self.tiles[x][y + 1].isActive and self.tiles[x][y + 1].isTileSolid() and self.tiles[x + 1][y + 1].isActive and self.tiles[x + 1][y + 1].isTileSolid():
      num6 -= 1
    else: 
      if self.tiles[x][y - 1].isActive and self.tiles[x][y - 1].isTileSolid() and not self.tiles[x][y - 1].isTileSolidTop() and self.tiles[x + 1][y - 1].isActive and self.tiles[x + 1][y - 1].isTileSolid() and not self.tiles[x + 1][y - 1].isTileSolidTop():
        num7 = 1
      else:
        if self.tiles[x - 1][y].isActive and self.tiles[x - 1][y].isTileSolid() and not self.tiles[x - 1][y].isTileSolidTop() and self.tiles[x - 1][y + 1].isActive and self.tiles[x - 1][y + 1].isTileSolid() and not self.tiles[x - 1][y + 1].isTileSolidTop():
          num7 = 2
        else:
          if not self.tiles[x + 1][y].isActive or not self.tiles[x + 1][y].isTileSolid() or self.tiles[x + 1][y].isTileSolidTop() or not self.tiles[x + 1][y + 1].isActive or not self.tiles[x + 1][y + 1].isTileSolid() or self.tiles[x + 1][y + 1].isTileSolidTop():
            return
          num5 -=1
          num7 = 3
    if self.tiles[num5][num6].isActive or self.tiles[num5 + 1][num6].isActive or self.tiles[num5][num6 + 1].isActive or self.tiles[num5 + 1][num6 + 1].isActive:
      return
    else:
      num8 = 36 * num7
      for k in range(2):
        for l in range(2):
          self.tiles[num5 + k][num6 + l] = self.tiles[num5 + k][num6 + l].copy()
          self.tiles[num5 + k][num6 + l].isActive = True
          self.tiles[num5 + k][num6 + l].tileType = tileType
          self.tiles[num5 + k][num6 + l].frameX = num8 + 18 * k
          self.tiles[num5 + k][num6 + l].frameY = 18 * l
        
  def place1x2Top(self, x, y, tileType):
    if self.tiles[x][y - 1].isActive and self.tiles[x][y - 1].isTileSolid() and not self.tiles[x][y - 1].isTileSolidTop() and not self.tiles[x][y + 1].isActive:
      self.tiles[x][y] = self.tiles[x][y].copy()
      self.tiles[x][y].isActive = True
      self.tiles[x][y].frameY = 0
      self.tiles[x][y].frameX = 0
      self.tiles[x][y].tileType = tileType
      
      self.tiles[x][y + 1] = self.tiles[x][y + 1].copy()
      self.tiles[x][y + 1].isActive = True
      self.tiles[x][y + 1].frameY = 18
      self.tiles[x][y + 1].frameX = 0
      self.tiles[x][y + 1].tileType = tileType
    
  def placePot(self, x, y, tileType):
    flag = True
    for i in range(x, x + 2):
      for j in range(y - 1, y + 1):
        if self.tiles[i][j].isActive:
          flag = False
          break
      if not self.tiles[i][y + 1].isActive or not self.tiles[i][y + 1].isTileSolid():
        flag = False
        break
    if flag:
      for i in range(2):
        for j in range(-1, 1):
          num = i * 18 + random.randint(0, 3) * 36
          num2 = (j + 1) * 18
          self.tiles[x + i][y + j] = self.tiles[x + i][y + j].copy()
          self.tiles[x + i][y + j].isActive = True
          self.tiles[x + i][y + j].frameX = num
          self.tiles[x + i][y + j].frameY = num2
          self.tiles[x + i][y + j].tileType = tileType
    
  def placeDoor(self, x, y, tileType):
    if self.tiles[x][y - 2].isActive and self.tiles[x][y - 2].isTileSolid() and self.tiles[x][y + 2].isActive and self.tiles[x][y + 2].isTileSolid():
      self.tiles[x][y - 1] = self.tiles[x][y - 1].copy()
      self.tiles[x][y - 1].isActive = True
      self.tiles[x][y - 1].tileType = 10
      self.tiles[x][y - 1].frameY = 0
      self.tiles[x][y - 1].frameX = random.randint(0, 3) * 18
      
      self.tiles[x][y] = self.tiles[x][y].copy()
      self.tiles[x][y].isActive = True
      self.tiles[x][y].tileType = 10
      self.tiles[x][y].frameY = 18
      self.tiles[x][y].frameX = random.randint(0, 3) * 18
      
      self.tiles[x][y + 1] = self.tiles[x][y + 1].copy()
      self.tiles[x][y + 1].isActive = True
      self.tiles[x][y + 1].tileType = 10
      self.tiles[x][y + 1].frameY = 36
      self.tiles[x][y + 1].frameX = random.randint(0, 3) * 18
    
  def placeOnTable1x1(self, x, y, tileType):
    flag = False
    if not self.tiles[x][y].isActive and self.tiles[x][y + 1].isActive and self.tiles[x][y + 1].isTileTable():
      flag = True
    if tileType == 78:
      if not self.tiles[x][y].isActive and self.tiles[x][y + 1].isActive and self.tiles[x][y + 1].isTileSolid():
        flag = True
    if flag:
      self.tiles[x][y] = self.tiles[x][y].copy()
      self.tiles[x][y].isActive = True
      self.tiles[x][y].frameX = 0
      self.tiles[x][y].frameY = 0
      self.tiles[x][y].tileType = tileType
      if tileType == 50:
        self.tiles[x][y].frameX = random.randint(0, 5) * 18
    
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
