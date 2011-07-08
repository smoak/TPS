"""
 Fair warning, this file is a beast.
"""

import logging, random

from game.tile import *
from util.math import *
from common.events import EventHook, ItemCreatedEventArgs, NewTileSquareEventArgs
import game.tile
from game.item import *
from util.item import ItemGenerator
from game.chest import Chest
from factory.projectile import ProjectileFactory

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
    self.projectileFactory = ProjectileFactory(self)
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
    self.projectiles = []
    self.waterLine = 0
    self.lavaLine = 0
    self.onItemCreated = EventHook()
    self.shadowOrbSmashed = False
    self.shadowOrbCount = 0
    self.noTileActions = False
    self.mergeUp = False
    self.mergeDown = False
    self.mergeLeft = False
    self.mergeRight = False
    self.onProjectileCreated = EventHook()
    self.onNewTileSquare = EventHook()

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
        self.tiles[x][y].frameNumber = 0
        self.tiles[x][y].tileType = 0
        if self.tiles[x][y].isTileSolid():
          self.tiles[x][y].isLighted = False
        self.squareTileFrame(coord, True)
    itemNum = -1
    if newItem:
      itemNum = self.getNextItemNum()
      self.items[itemNum] = newItem
      self.__raiseItemCreatedEvent(newItem, itemNum)
  
  def __raiseProjectileCreatedEvent(self, projectile):
    self.onProjectileCreated.fire(projectile=projectile)  
  
  def __raiseItemCreatedEvent(self, item, itemNum):
    self.onItemCreated.fire(eventArgs=ItemCreatedEventArgs(item, itemNum))
    
  def __raiseNewTileSquareEvent(self, tileX, tileY, size):
    self.onNewTileSquare.fire(eventArgs=NewTileSquareEventArgs(tileX, tileY, size))

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

  def __newItem(self, x, y, width, height, itemType, stack):
    newItemNum = self.getNextItemNum()
    # should probably somehow move this to an easier place?
    newItem = self.itemGenerator.generateNewItem(x, y, width, height, itemType, stack)
    self.items[newItemNum] = newItem
    self.__raiseItemCreatedEvent(newItem, newItemNum)
    
  def check1x2(self, x, y, tileType):
    if self.destroyObject:
      return
    num = y
    flag = True
    if self.tiles[x][num].frameY == 18:
      num -= 1
    if self.tiles[x][num].frameY == 0 and self.tiles[x][num + 1].frameY == 18 and self.tiles[x][num].tileType == tileType and self.tiles[x][num + 1].tileType == tileType:
      flag = False
    if not self.tiles[x][num + 2].isActive or not self.tiles[x][num + 2].isTileSolid():
      flag = True
    if self.tiles[x][num + 2].tileType != 2 and self.tiles[x][num].tileType == 20:
      flag = True
    if flag:
      self.destroyObject = True
      if self.tiles[x][num].tileType == tileType:
        self.killTile((x, num), False, False, False)
      if self.tiles[x][num + 1].tileType == tileType:
        self.killTile((num, num + 1), False, False, False)
      if tileType == 15:
        self.__newItem(x * 16, num * 16, 32, 32, 34, 1)
      self.destroyObject = False
    
  def tileFrame(self, x, y, resetFrame = False, noBreak = False):
    if x >= 0 and y >= 0 and x < self.width and y < self.height:
      tile = self.tiles[x][y]
      if tile.liquid > 0:
        self.addWater(x, y)
      if tile.isActive:
        if noBreak and tile.isImportant():
          return
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
          return
        self.mergeUp = False
        self.mergeDown = False
        self.mergeLeft = False
        self.mergeRight = False
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
            return
          if (num4 >= 0 and num4 in game.tile.SOLID_TILES and not (num4 in game.tile.NO_ATTACH_TILES)) or (num4 == 5 and num == 5 and num6 == 5):
            self.tiles[x][y] = self.tiles[x][y].copy()
            self.tiles[x][y].frameX = 22
            return
          if (num5 >= 0 and num5 in game.tile.SOLID_TILES and not (num5 in game.tile.NO_ATTACH_TILES)) or (num5 == 5 and num3 == 5 and num8 == 5):
            self.tiles[x][y] = self.tiles[x][y].copy()
            self.tiles[x][y].frameX = 44
            return
          self.killTile((x, y), False, False, False)
          return
        else:
          if newTileType == 80:
            self.cactusFrame(x, y)
            return
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
                  newItemNum = self.getNextItemNum()
                  # should probably somehow move this to an easier place?
                  newItem = self.itemGenerator.generateNewItem(num10 * 16, num11 * 16, 32, 32, 29, 1)
                  self.items[newItemNum] = newItem
                  self.__raiseItemCreatedEvent(newItem, newItemNum)
                else:
                  if newTileType == 31:
                    if random.randint(0, 2) == 0:
                      self.spawnMeteor = True
                    num12 = random.randint(0, 5)
                    if not self.shadowOrbSmashed:
                      num12 = 0
                    if num12 == 0:
                      newItemNum = self.getNextItemNum()
                      # should probably somehow move this to an easier/better place?
                      newItem = self.itemGenerator.generateNewItem(num10 * 16, num11 * 16, 32, 32, 96, 1)
                      self.items[newItemNum] = newItem
                      self.__raiseItemCreatedEvent(newItem, newItemNum)
                      stack = random.randint(25, 51)
                      newItemNum = self.getNextItemNum()
                      # should probably somehow move this to an easier/better place?
                      newItem = self.itemGenerator.generateNewItem(num10 * 16, num11 * 16, 32, 32, 97, stack)
                      self.items[newItemNum] = newItem
                      self.__raiseItemCreatedEvent(newItem, newItemNum)
                    else:
                      if num12 == 1:
                        self.__newItem(num10 * 16, num11 * 16, 32, 32, 64, 1)
                      if num12 == 2:
                        self.__newItem(num10 * 16, num11 * 16, 32, 32, 162, 1)
                      if num12 == 3:
                        self.__newItem(num10 * 16, num11 * 16, 32, 32, 115, 1)
                      if num12 == 4:
                        self.__newItem(num10 * 16, num11 * 16, 32, 32, 111, 1)
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
                self.destroyObject = False
              return
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
                    self.__newItem(x * 16, y * 16, 16, 16, 25, 1)
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
                    self.__newItem(x * 16, y * 16, 16, 16, 25, 1)
                  num18 = num10
                  if num17 == -1:
                    num18 = num10 - 1
                  for l in range(num18, num18 + 2):
                    for m in range(num11, num11 + 3):
                      if not flag:
                        if self.tiles[l][m].tileType != 11 or not self.tiles[l][m].isActive:
                          self.destroyObject = True
                          self.__newItem(x * 16, y * 16, 16, 16, 25, 1)
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
              if newTileType == 55 or newTileType == 85:
                self.checkSign(x, y, newTileType)
                return
              if newTileType == 79:
                self.check4x2(x, y, newTileType)
                return
              if newTileType == 85:
                self.check2x2(x, y, newTileType)
                return
              if newTileType == 81:
                if num4 != -1 or num2 != -1 or num5 != -1:
                  self.killTile((x, y), False, False, False)
                  return
                if num7 < 0 or not num7 in game.tile.SOLID_TILES:
                  self.killTile((x, y), False, False, False)
                return
              else:
                if newTileType in game.tile.ALCHEMY_TILES:
                  self.checkAlch(x, y)
                  return
            if newTileType == 72:
              if num7 != newTileType and num7 != 70:
                self.killTile((x, y), False, False, False)
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
                if num7 != 2:
                  self.killTile((x, y), False, False, False)
                if num4 != newTileType and num5 != newTileType:
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
                elif num4 != newTileType:
                  self.tiles[x][y] = self.tiles[x][y].copy()
                  if self.tiles[x][y].frameNumber == 0:
                    self.tiles[x][y].frameX = 0
                    self.tiles[x][y].frameY = 132
                  if self.tiles[x][y].frameNumber == 1:
                    self.tiles[x][y].frameX = 0
                    self.tiles[x][y].frameY = 154
                  if self.tiles[x][y].frameNumber == 2:
                    self.tiles[x][y].frameX = 0
                    self.tiles[x][y].frameY = 176
                elif num5 != newTileType:
                  self.tiles[x][y] = self.tiles[x][y].copy()
                  if self.tiles[x][y].frameNumber == 0:
                    self.tiles[x][y].frameX = 66
                    self.tiles[x][y].frameY = 132
                  if self.tiles[x][y].frameNumber == 1:
                    self.tiles[x][y].frameX = 66
                    self.tiles[x][y].frameY = 154
                  if self.tiles[x][y].frameNumber == 2:
                    self.tiles[x][y].frameX = 66
                    self.tiles[x][y].frameY = 176
                else:
                  self.tiles[x][y] = self.tiles[x][y].copy()
                  if self.tiles[x][y].frameNumber == 0:
                    self.tiles[x][y].frameX = 88
                    self.tiles[x][y].frameY = 132
                  if self.tiles[x][y].frameNumber == 1:
                    self.tiles[x][y].frameX = 88
                    self.tiles[x][y].frameY = 154
                  if self.tiles[x][y].frameNumber == 2:
                    self.tiles[x][y].frameX = 88
                    self.tiles[x][y].frameY = 176
              if self.tiles[x][y].frameX == 66 and (self.tiles[x][y].frameY in [0, 22, 44]):
                if num4 != newTileType and num5 != newTileType:
                  self.killTile((x, y), False, False, False)
              else:
                if num7 == -1 or num7 == 23:
                  self.killTile((x, y), False, False, False)
                else:
                  if num2 != newTileType and self.tiles[x][y].frameY < 198 and ((self.tiles[x][y].frameX != 22 and self.tiles[x][y].frameX != 44) or self.tiles[x][y].frameY < 132):
                    if num4 == newTileType or num5 != newTileType:
                      if num7 == newTileType:
                        if num4 == newTileType and num5 == newTileType:
                          self.tiles[x][y] = self.tiles[x][y].copy()
                          if self.tiles[x][y].frameNumber == 0:
                            self.tiles[x][y].frameX = 132
                            self.tiles[x][y].frameY = 132
                          if self.tiles[x][y].frameNumber == 1:
                            self.tiles[x][y].frameX = 132
                            self.tiles[x][y].frameY = 154
                          if self.tiles[x][y].frameNumber == 2:
                            self.tiles[x][y].frameX = 132
                            self.tiles[x][y].frameY = 176
                        elif num4 == newTileType:
                          self.tiles[x][y] = self.tiles[x][y].copy()
                          if self.tiles[x][y].frameNumber == 0:
                            self.tiles[x][y].frameX = 132
                            self.tiles[x][y].frameY = 0
                          if self.tiles[x][y].frameNumber == 1:
                            self.tiles[x][y].frameX = 132
                            self.tiles[x][y].frameY = 22
                          if self.tiles[x][y].frameNumber == 2:
                            self.tiles[x][y].frameX = 132
                            self.tiles[x][y].frameY = 44
                        elif num5 == newTileType:
                          self.tiles[x][y] = self.tiles[x][y].copy()
                          if self.tiles[x][y].frameNumber == 0:
                            self.tiles[x][y].frameX = 132
                            self.tiles[x][y].frameY = 66
                          if self.tiles[x][y].frameNumber == 1:
                            self.tiles[x][y].frameX = 132
                            self.tiles[x][y].frameY = 88
                          if self.tiles[x][y].frameNumber == 2:
                            self.tiles[x][y].frameX = 132
                            self.tiles[x][y].frameY = 110
                      else:
                        if num4 == newTileType and num5 == newTileType:
                          self.tiles[x][y] = self.tiles[x][y].copy()
                          if self.tiles[x][y].frameNumber == 0:
                            self.tiles[x][y].frameX = 154
                            self.tiles[x][y].frameY = 132
                          if self.tiles[x][y].frameNumber == 1:
                            self.tiles[x][y].frameX = 154
                            self.tiles[x][y].frameY = 154
                          if self.tiles[x][y].frameNumber == 2:
                            self.tiles[x][y].frameX = 154
                            self.tiles[x][y].frameY = 176
                        elif num4 == newTileType:
                          self.tiles[x][y] = self.tiles[x][y].copy()
                          if self.tiles[x][y].frameNumber == 0:
                            self.tiles[x][y].frameX = 154
                            self.tiles[x][y].frameY = 0
                          if self.tiles[x][y].frameNumber == 1:
                            self.tiles[x][y].frameX = 154
                            self.tiles[x][y].frameY = 22
                          if self.tiles[x][y].frameNumber == 2:
                            self.tiles[x][y].frameX = 154
                            self.tiles[x][y].frameY = 44
                        elif num5 == newTileType:
                          self.tiles[x][y] = self.tiles[x][y].copy()
                          if self.tiles[x][y].frameNumber == 0:
                            self.tiles[x][y].frameX = 154
                            self.tiles[x][y].frameY = 66
                          if self.tiles[x][y].frameNumber == 1:
                            self.tiles[x][y].frameX = 154
                            self.tiles[x][y].frameY = 88
                          if self.tiles[x][y].frameNumber == 2:
                            self.tiles[x][y].frameX = 154
                            self.tiles[x][y].frameY = 110
                    else:
                      self.tiles[x][y] = self.tiles[x][y].copy()
                      if self.tiles[x][y].frameNumber == 0:
                        self.tiles[x][y].frameX = 110
                        self.tiles[x][y].frameY = 0
                      if self.tiles[x][y].frameNumber == 1:
                        self.tiles[x][y].frameX = 110
                        self.tiles[x][y].frameY = 22
                      if self.tiles[x][y].frameNumber == 2:
                        self.tiles[x][y].frameX = 110
                        self.tiles[x][y].frameY = 44
              tmpFrameX = self.tiles[x][y].frameX
              tmpFrameY = self.tiles[x][y].frameY
            if self.tiles[x][y].isImportant():
              return
            num22 = 0
            if resetFrame:
              num22 = random.randint(0, 3)
              self.tiles[x][y] = self.tiles[x][y].copy()
              self.tiles[x][y].frameNumber = num22
            else:
              num22 = self.tiles[x][y].frameNumber
            if newTileType == 0:
              for n in range(86):
                if n in [1, 6, 7, 8, 9, 22, 25, 37, 40, 53, 56, 59]:
                  if num2 == n:
                    self.tileFrame(x, y - 1, False, False)
                    if self.mergeDown:
                      num2 = newTileType
                  if num7 == n:
                    self.tileFrame(x, y + 1, False, False)
                    if self.mergeUp:
                      num7 = newTileType
                  if num4 == n:
                    self.tileFrame(x - 1, y, False, False)
                    if self.mergeRight:
                      num4 = newTileType
                  if num5 == n:
                    self.tileFrame(x + 1, y, False, False)
                    if self.mergeLeft:
                      num5 = newTileType
                  if num == n:
                    num = newTileType
                  if num3 == n:
                    num3 = newTileType
                  if num6 == n:
                    num6 = newTileType
                  if num8 == n:
                    num8 = newTileType
              if num2 == 2:
                num2 = newTileType
              if num7 == 2:
                num7 = newTileType
              if num4 == 2:
                num4 = newTileType
              if num5 == 2:
                num5 = newTileType
              if num == 2:
                num = newTileType
              if num3 == 2:
                num3 = newTileType
              if num6 == 2:
                num6 = newTileType
              if num8 == 2:
                num8 = newTileType
              if num2 == 23:
                num2 = newTileType
              if num7 == 23:
                num7 = newTileType
              if num4 == 23:
                num4 = newTileType
              if num5 == 23:
                num5 = newTileType
              if num == 23:
                num = newTileType
              if num3 == 23:
                num3 = newTileType
              if num6 == 23:
                num6 = newTileType
              if num8 == 23:
                num8 = newTileType
            else:
              if newTileType == 57:
                if num2 == 58:
                  self.tileFrame(x, y - 1, False, False)
                  if self.mergeDown:
                    num2 = newTileType
                if num7 == 58:
                  self.tileFrame(x, y + 1, False, False)
                  if self.mergeUp:
                    num7 = newTileType
                if num4 == 48:
                  self.tileFrame(x - 1, y, False, False)
                  if self.mergeRight:
                    num4 = newTileType
                if num5 == 58:
                  self.tileFrame(x + 1, y, False, False)
                  if self.mergeLeft:
                    num5 = newTileType
                if num == 58:
                  num = newTileType
                if num3 == 58:
                  num3 = newTileType
                if num6 == 58:
                  num6 = newTileType
                if num8 == 58:
                  num8 = newTileType
              else:
                if newTileType == 59:
                  if num2 == 60:
                    num2 = newTileType
                  if num7 == 60:
                    num7 = newTileType
                  if num4 == 60:
                    num4 = newTileType
                  if num5 == 60:
                    num5 = newTileType
                  if num == 60:
                    num = newTileType
                  if num3 == 60:
                    num3 = newTileType
                  if num6 == 60:
                    num6 = newTileType
                  if num8 == 60:
                    num8 = newTileType
                  if num2 == 70:
                    num2 = newTileType
                  if num7 == 70:
                    num7 = newTileType
                  if num4 == 70:
                    num4 = newTileType
                  if num5 == 70:
                    num5 = newTileType
                  if num == 70:
                    num = newTileType
                  if num3 == 70:
                    num3 = newTileType
                  if num6 == 70:
                    num6 = newTileType
                  if num8 == 70:
                    num8 = newTileType
              if newTileType in [1, 6, 7, 8, 9, 22, 25, 37, 40, 53, 56, 59]:
                if num2 == 0:
                  num2 = -2
                if num7 == 0:
                  num7 = -2
                if num4 == 0:
                  num4 = -2
                if num5 == 0:
                  num5 = -2
                if num == 0:
                  num = -2
                if num3 == 0:
                  num3 = -2
                if num6 == 0:
                  num6 = -2
                if num8 == 0:
                  num8 = -2
              else:
                if newTileType == 58:
                  if num2 == 57:
                    num2 = -2
                  if num7 == 57:
                    num7 = -2
                  if num4 == 57:
                    num4 = -2
                  if num5 == 57:
                    num5 = -2
                  if num == 57:
                    num = -2
                  if num3 == 57:
                    num3 = -2
                  if num6 == 57:
                    num6 = -2
                  if num8 == 57:
                    num8 = -2
                else:
                  if newTileType == 59:
                    if num2 == 1:
                      num2 = -2 									 									
                    if num7 == 1: 									 										
                      num7 = -2 									 									
                    if num4 == 1: 									 										
                      num4 = -2 									 									
                    if num5 == 1: 									 										
                      num5 = -2 									 									
                    if num == 1: 									 										
                      num = -2 									 									
                    if num3 == 1: 									 										
                      num3 = -2 									 									
                    if num6 == 1: 									 										
                      num6 = -2 									 									
                    if num8 == 1: 									 										
                      num8 = -2 									
              if newTileType == 32 and num7 == 23:
                num7 = newTileType
              if newTileType == 69 and num7 == 60:
                num7 = newTileType
              if newTileType == 51:
                if num2 > -1 and not num2 in game.tile.NO_ATTACH_TILES:
                  num2 = newTileType
                if num7 > -1 and not num7 in game.tile.NO_ATTACH_TILES:
                  num7 = newTileType
                if num4 > -1 and not num4 in game.tile.NO_ATTACH_TILES:
                  num4 = newTileType
                if num5 > -1 and not num5 in game.tile.NO_ATTACH_TILES:
                  num5 = newTileType
                if num > -1 and not num in game.tile.NO_ATTACH_TILES:
                  num = newTileType
                if num3 > -1 and not num3 in game.tile.NO_ATTACH_TILES:
                  num3 = newTileType
                if num6 > -1 and not num6 in game.tile.NO_ATTACH_TILES:
                  num6 = newTileType
                if num8 > -1 and not num8 in game.tile.NO_ATTACH_TILES:
                  num8 = newTileType
              if num2 > -1 and not num2 in game.tile.SOLID_TILES and num2 != newTileType:
                num2 = -1
              if num7 > -1 and not num7 in game.tile.SOLID_TILES and num7 != newTileType:
                num7 = -1
              if num4 > -1 and not num4 in game.tile.SOLID_TILES and num4 != newTileType:
                num4 = -1
              if num5 > -1 and not num5 in game.tile.SOLID_TILES and num5 != newTileType:
                num5 = -1
              if num > -1 and not num in game.tile.SOLID_TILES and num != newTileType:
                num = -1
              if num3 > -1 and not num3 in game.tile.SOLID_TILES and num3 != newTileType:
                num3 = -1
              if num6 > -1 and not num6 in game.tile.SOLID_TILES and num6 != newTileType:
                num6 = -1
              if num8 > -1 and not num8 in game.tile.SOLID_TILES and num8 != newTileType:
                num8 = -1
              if newTileType in [2, 23, 60, 70]:
                num24 = 0
                if newTileType in [60, 70]:
                  num24 = 59
                if newTileType == 2:
                  if num2 == 23:
                    num2 = 0
                  if num7 == 23:
                    num7 = 0
                  if num4 == 23:
                    num4 = 0
                  if num5 == 23:
                    num5 = 0
                  if num == 23:
                    num = 0
                  if num3 == 23:
                    num3 = 0
                  if num6 == 23:
                    num6 = 0
                  if num8 == 23:
                    num8 = 0
                if newTileType == 23:
                  if num2 == 2:
                    num2 = 0
                  if num7 == 2:
                    num7 = 0
                  if num4 == 2:
                    num4 = 0
                  if num5 == 2:
                    num5 = 0
                  if num == 2:
                    num = 0
                  if num3 == 2:
                    num3 = 0
                  if num6 == 2:
                    num6 = 0
                  if num8 == 2:
                    num8 = 0
                if num2 != newTileType and num2 != num24 and (num7 == newTileType or num7 == num24):
                  if num4 == num24 and num5 == newTileType:
                    if num22 == 0:
                      tmpFrameX = 0
                      tmpFrameY = 198
                    if num22 == 1:
                      tmpFrameX = 18
                      tmpFrameY = 198
                    if num22 == 2:
                      tmpFrameX = 36
                      tmpFrameY = 198
                  if num4 == newTileType and num5 == num24:
                    if num22 == 0:
                      tmpFrameX = 54
                      tmpFrameY = 198
                    if num22 == 1:
                      tmpFrameX = 72
                      tmpFrameY = 198
                    if  num22 == 2:
                      tmpFrameX = 90
                      tmpFrameY = 198
                else:
                  if num7 != newTileType and num7 != num24 and (num2 == newTileType or num2 == num24):
                    if num4 == num24 and num5 == newTileType:
                      if num22 == 0:
                        tmpFrameX = 0
                        tmpFrameY = 216
                      if num22 == 1:
                        tmpFrameX = 18
                        tmpFrameY = 216
                      if num22 == 2:
                        tmpFrameX = 36
                        tmpFrameY = 216 
                    else:
                      if num4 == newTileType and num5 == num24:
                        if num22 == 0:
                          tmpFrameX = 54
                          tmpFrameY = 216
                        if num22 == 1:
                          tmpFrameX = 72
                          tmpFrameY = 216
                        if num22 == 2:
                          tmpFrameX = 90
                          tmpFrameY = 216 
                  else:
                    if num4 != newTileType and num4 != num24 and (num5 == newTileType or num5 == num24):
                      if num2 == num24 and num7 == newTileType:
                        if num22 == 0:
                          tmpFrameX = 72
                          tmpFrameY = 144
                        if num22 == 1:
                          tmpFrameX = 72
                          tmpFrameY = 162
                        if num22 == 2:
                          tmpFrameX = 72
                          tmpFrameY = 180
                      else:
                        if num7 == newTileType and num5 == num2:
                          if num22 == 0:
                            tmpFrameX = 72
                            tmpFrameY = 90
                          if num22 == 1:
                            tmpFrameX = 72
                            tmpFrameY = 108
                          if num22 == 2:
                            tmpFrameX = 72
                            tmpFrameY = 126
                    else:
                      if num5 != newTileType and num5 != num24 and (num4 == newTileType or num4 == num24):
                        if num2 == num24 and num7 == newTileType:
                          if num22 == 0:
                            tmpFrameX = 90
                            tmpFrameY = 144
                          if num22 == 1:
                            tmpFrameX = 90
                            tmpFrameY = 162
                          if num22 == 2:
                            tmpFrameX = 90
                            tmpFrameY = 180
                        else:
                          if num7 == newTileType and num5 == num2:
                            if num22 == 0:
                              tmpFrameX = 90
                              tmpFrameY = 90
                            if num22 == 1:
                              tmpFrameX = 90
                              tmpFrameY = 108
                            if num22 == 2:
                              tmpFrameX = 90
                              tmpFrameY = 126
                      else:
                        if num2 == newTileType and num7 == newTileType and num4 == newTileType and num5 == newTileType:
                          if num != newTileType and num3 != newTileType and num6 != newTileType and num8 != newTileType:
                            if num8 == num24:
                              if num22 == 0:
                                tmpFrameX = 108
                                tmpFrameY = 324
                              if num22 == 1:
                                tmpFrameX = 126
                                tmpFrameY = 324
                              if num22 == 2:
                                tmpFrameX = 144
                                tmpFrameY = 324
                            else:
                              if num3 == num24:
                                if num22 == 0:
                                  tmpFrameX = 108
                                  tmpFrameY = 342
                                if num22 == 1:
                                  tmpFrameX = 126
                                  tmpFrameY = 342
                                if num22 == 2:
                                  tmpFrameX = 144
                                  tmpFrameY = 342
                              else:
                                if num6 == num24:
                                  if num22 == 0:
                                    tmpFrameX = 108
                                    tmpFrameY = 360
                                  if num22 == 1:
                                    tmpFrameX = 126
                                    tmpFrameY = 360
                                  if num22 == 2:
                                    tmpFrameX = 144
                                    tmpFrameY = 360
                                else:
                                  if num == num24:
                                    if num22 == 0:
                                      tmpFrameX = 108
                                      tmpFrameY = 378
                                    if num22 == 1:
                                      tmpFrameX = 126
                                      tmpFrameY = 378
                                    if num22 == 2:
                                      tmpFrameX = 144
                                      tmpFrameY = 378
                                  else:
                                    if num22 == 0:
                                      tmpFrameX = 144
                                      tmpFrameY = 234
                                    if num22 == 1:
                                      tmpFrameX = 198
                                      tmpFrameY = 234
                                    if num22 == 2:
                                      tmpFrameX = 252
                                      tmpFrameY = 234
                          else:
                            if num != newTileType and num8 != newTileType:
                              if num22 == 0:
                                tmpFrameX = 36
                                tmpFrameY = 306
                              if num22 == 1:
                                tmpFrameX = 54
                                tmpFrameY = 306
                              if num22 == 2:
                                tmpFrameX = 72
                                tmpFrameY = 306
                            else:
                              if num3 != newTileType and num6 != newTileType:
                                if num22 == 0:
                                  tmpFrameX = 90
                                  tmpFrameY = 306
                                if num22 == 1:
                                  tmpFrameX = 108
                                  tmpFrameY = 306
                                if num22 == 2:
                                  tmpFrameX = 126
                                  tmpFrameY = 306
                              else:
                                if num != newTileType and num3 == newTileType and num6 == newTileType and num8 == newTileType:
                                  if num22 == 0:
                                    tmpFrameX = 54
                                    tmpFrameY = 108
                                  if num22 == 1:
                                    tmpFrameX = 54
                                    tmpFrameY = 144
                                  if num22 == 2:
                                    tmpFrameX = 54
                                    tmpFrameY = 180
                                else:
                                  if num == newTileType and num3 != newTileType and num6 == newTileType and num8 == newTileType:
                                    if num22 == 0:
                                      tmpFrameX = 36
                                      tmpFrameY = 108
                                    if num22 == 1:
                                      tmpFrameX = 36
                                      tmpFrameY = 144
                                    if num22 == 2:
                                      tmpFrameX = 36
                                      tmpFrameY = 180
                                  else:
                                    if num == newTileType and num3 == newTileType and num6 != newTileType and num8 == newTileType:
                                      if num22 == 0:
                                        tmpFrameX = 54
                                        tmpFrameY = 90
                                      if num22 == 1:
                                        tmpFrameX = 54
                                        tmpFrameY = 126
                                      if num22 == 2:
                                        tmpFrameX = 54
                                        tmpFrameY = 162
                                    else:
                                      if num == newTileType and num3 == newTileType and num6 == newTileType and num8 != newTileType:
                                        if num22 == 0:
                                          tmpFrameX = 36
                                          tmpFrameY = 90
                                        if num22 == 1:
                                          tmpFrameX = 36
                                          tmpFrameY = 126
                                        if num22 == 2:
                                          tmpFrameX = 36
                                          tmpFrameY = 162
                        else:
                          if num2 == newTileType and num7 == num24 and num4 == newTileType and num5 == newTileType and num == -1 and num3 == -1:
                            if num22 == 0:
                              tmpFrameX = 108
                              tmpFrameY = 18
                            if num22 == 1:
                              tmpFrameX = 126
                              tmpFrameY = 18
                            if num22 == 2:
                              tmpFrameX = 144
                              tmpFrameY = 18
                          else:
                            if num2 == num24 and num7 == newTileType and num4 == newTileType and num5 == newTileType and num6 == -1 and num8 == -1:
                              if num22 == 0:
                                tmpFrameX = 108
                                tmpFrameY = 36
                              if num22 == 1:
                                tmpFrameX = 126
                                tmpFrameY = 36
                              if num22 == 2:
                                tmpFrameX = 144
                                tmpFrameY = 36
                            else:
                              if num2 == newTileType and num7 == newTileType and num4 == num24 and num5 == newTileType and num3 == -1 and num8 == -1:
                                if num22 == 0:
                                  tmpFrameX = 198
                                  tmpFrameY = 0
                                if num22 == 1:
                                  tmpFrameX = 198
                                  tmpFrameY = 18
                                if num22 == 2:
                                  tmpFrameX = 198
                                  tmpFrameY = 36
                              else:
                                if num2 == newTileType and num7 == newTileType and num4 == newTileType and num5 == num24 and num == -1 and num6 == -1:
                                  if num22 == 0:
                                    tmpFrameX = 180
                                    tmpFrameY = 0
                                  if num22 == 1:
                                    tmpFrameX = 180
                                    tmpFrameY = 18
                                  if num22 == 2:
                                    tmpFrameX = 180
                                    tmpFrameY = 36
                                else:
                                  if num2 == newTileType and num7 == num24 and num4 == newTileType and num5 == newTileType:
                                    if num3 != -1:
                                      if num22 == 0:
                                        tmpFrameX = 54
                                        tmpFrameY = 108
                                      if num22 == 1:
                                        tmpFrameX = 54
                                        tmpFrameY = 144
                                      if num22 == 2:
                                        tmpFrameX = 54
                                        tmpFrameY = 180
                                    else:
                                      if num != -1:
                                        if num22 == 0:
                                          tmpFrameX = 36
                                          tmpFrameY = 108
                                        if num22 == 1:
                                          tmpFrameX = 36
                                          tmpFrameY = 144
                                        if num22 == 2:
                                          tmpFrameX = 36
                                          tmpFrameY = 180
                                  else:
                                    if num2 == num24 and num7 == newTileType and num4 == newTileType and num5 == newTileType:
                                      if num8 != -1:
                                        if num22 == 0:
                                          tmpFrameX = 54
                                          tmpFrameY = 90
                                        if num22 == 1:
                                          tmpFrameX = 54
                                          tmpFrameY = 126
                                        if num22 == 2:
                                          tmpFrameX = 54
                                          tmpFrameY = 162
                                      else:
                                        if num6 != -1:
                                          if num22 == 0:
                                            tmpFrameX = 36
                                            tmpFrameY = 90
                                          if num22 == 1:
                                            tmpFrameX = 36
                                            tmpFrameY = 126
                                          if num22 == 2:
                                            tmpFrameX = 36
                                            tmpFrameY = 162
                                    else:
                                      if num2 == newTileType and num7 == newTileType and num4 == newTileType and num5 == num24:
                                        if num != -1:
                                          if num22 == 0:
                                            tmpFrameX = 54
                                            tmpFrameY = 90
                                          if num22 == 1:
                                            tmpFrameX = 54
                                            tmpFrameY = 126
                                          if num22 == 2:
                                            tmpFrameX = 54
                                            tmpFrameY = 162
                                        else:
                                          if num6 != -1:
                                            if num22 == 0:
                                              tmpFrameX = 54
                                              tmpFrameY = 108
                                            if num22 == 1:
                                              tmpFrameX = 54
                                              tmpFrameY = 144
                                            if num22 == 2:
                                              tmpFrameX = 54
                                              tmpFrameY = 180
                                      else:
                                        if num2 == newTileType and num7 == newTileType and num4 == num24 and num5 == newTileType:
                                          if num3 != -1:
                                            if num22 == 0:
                                              tmpFrameX = 36
                                              tmpFrameY = 90
                                            if num22 == 1:
                                              tmpFrameX = 36
                                              tmpFrameY = 126
                                            if num22 == 2:
                                              tmpFrameX = 36
                                              tmpFrameY = 162
                                          else:
                                            if num8 != -1:
                                              if num22 == 0:
                                                tmpFrameX = 36
                                                tmpFrameY = 108
                                              if num22 == 1:
                                                tmpFrameX = 36
                                                tmpFrameY = 144
                                              if num22 == 2:
                                                tmpFrameX = 36
                                                tmpFrameY = 180
                                        else:
                                          if (num2 == num24 and num7 == newTileType and num4 == newTileType and num5 == newTileType) or (num2 == newTileType and num7 == num24 and num4 == newTileType and num5 == newTileType) or (num2 == newTileType and num7 == newTileType and num4 == num24 and num5 == newTileType) or (num2 == newTileType and num7 == newTileType and num4 == newTileType and num5 == num24):
                                            if num22 == 0:
                                              tmpFrameX = 18
                                              tmpFrameY = 18
                                            if num22 == 1:
                                              tmpFrameX = 36
                                              tmpFrameY = 18
                                            if num22 == 2:
                                              tmpFrameX = 54
                                              tmpFrameY = 18
                if (num2 == newTileType or num2 == num24) and (num7 == newTileType or num7 == num24) and (num4 == newTileType or num4 == num24) and (num5 == newTileType or num5 == num24):
                  pass
              self.tiles[x][y] = self.tiles[x][y].copy()
              self.tiles[x][y].frameX = tmpFrameX
              self.tiles[x][y].frameY = tmpFrameY
              if newTileType in [52, 62]:
                if not self.tiles[x][y - 1].isActive:
                  num2 = -1
                else:
                  num2 = self.tiles[x][y - 1].tileType
                if num2 != newTileType and num2 != 2 and num2 != 60:
                  self.killTile((x, y), False, False, False)
              if not self.noTileActions and (newTileType == TileType.Sand or ((newTileType == 59 or newTileType == 57) and random.randint(0, 5) == 0)):
                if not self.tiles[x][y + 1].isActive:
                  flag4 = True
                  if self.tiles[x][y - 1].isActive and self.tiles[x][y - 1].tileType == 21:
                    flag4 = False
                  if flag4:
                    type2 = 31
                    if newTileType == 59:
                      type2 = 39
                    if newTileType == 57:
                      type2 = 40
                    self.tiles[x][y] = self.tiles[x][y].copy()
                    self.tiles[x][y].isActive = False
                    p = self.projectileFactory.newProjectile(x * 16 + 8, y * 16 + 8, 0, 0.41, type2, 10, 0, 255)
                    self.projectiles.append(p)
                    self.__raiseProjectileCreatedEvent(p)
                    # send tile square...  -1, x, y, 1
                    self.__raiseNewTileSquareEvent(x, y, 1)
                    self.squareTileFrame((x, y), True)
              if tmpFrameX != frameX and tmpFrameY != frameY and frameX >= 0 and frameY >= 0:
                oldMergeUp = self.mergeUp
                oldMergeDown = self.mergeDown
                oldMergeLeft = self.mergeLeft
                oldMergeRight = self.mergeRight
                self.tileFrame(x - 1, y, False, False)
                self.tileFrame(x + 1, y, False, False)
                self.tileFrame(x, y - 1, False, False)
                self.tileFrame(x, y + 1, False, False)
                self.mergeUp = oldMergeUp
                self.mergeDown = oldMergeDown
                self.mergeLeft = oldMergeLeft
                self.mergeRight = oldMergeRight

  def check1x2Top(self, x, y, tileType):
    if self.destroyObject:
      return  
    num = y
    flag = True
    if self.tiles[x][y].frameY == 18:
      num -= 1
    if self.tiles[x][num].frameY == 0 and self.tiles[x][num + 1].frameY == 18 and self.tiles[x][num].tileType == tileType and self.tiles[x][num + 1].tileType == tileType:
      flag = False
    if not self.tiles[x][num - 1].isActive or not self.tiles[x][num - 1].isTileSolid() or self.tiles[x][num - 1].isTileSolidTop():
      flag = False
    if flag:
      self.destroyObject = True
      if self.tiles[x][num].tileType == tileType:
        self.killTile((x, num), False, False, False)
      if self.tiles[x][num + 1].tileType == tileType:
        self.killTile((x, num + 1), False, False, False)
      if tileType == 42:
        self.__newItem(x * 16, num * 16, 32, 32, 136, 1)
      self.destroyObject = False
  
  def plantCheck(self, x, y):
    num = -1
    tileType = self.tiles[x][y].tileType
    num2 = x - 1
    num3 = x + 1
    width = self.width
    num4 = y - 1
    if y + 1 >= self.height:
      num = tileType
    if num2 >= 0 and self.tiles[num2][y].isActive:
      num = self.tiles[num2][y].tileType
    if num3 < self.width and self.tiles[num3][y].isActive:
      num = self.tiles[num3][y].tileType
    if num4 >= 0 and self.tiles[x][num4].isActive:
      num = self.tiles[x][num4].tileType
    if y + 1 < self.height and self.tiles[x][y + 1].isActive:
      num = self.tiles[x][y + 1].tileType
    if num2 >= 0 and num4 >= 0 and self.tiles[num2][num4].isActive:
      num = self.tiles[num2][num4].tileType
    if num3 < self.width and num4 >= 0 and self.tiles[num3][num4].isActive:
      num = self.tiles[num3][num4].tileType
    if num2 >= 0 and y + 1 < self.height and self.tiles[num2][y + 1].isActive:
      num = self.tiles[num2][y + 1].tileType
    if num3 < self.width and y + 1 < self.height and self.tiles[num3][y + 1].isActive:
      num = self.tiles[num3][y + 1].tileType
    if (tileType == 3 and num != 2 and num != 78) or (tileType == 24 and num != 23) or (tileType == 61 and num != 60) or (tileType == 71 and num != 70) or (tileType == 73 and num != 2 and num != 78) or (tileType == 74 and num != 60):
      self.killTile((x, y), False, False, False)
      
  def addWater(self, x, y):
    if self.tiles[x][y].checkingLiquid:
      return
    if x >= self.width - 5 or y >= self.height - 5:
      return
    if x < 5 or y < 5:
      return
    if self.tiles[x][y].liquid == 0:
      return
   
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

  def placeTile(self, x, y, tileType, mute = False, forced = False, plr = -1, style = 0):
    if x < 0 or y < 0 or x > self.width or y > self.height or tileType >= 86:
      return
    tile = self.tiles[x][y].copy()
    if forced or self.emptyTile(x, y, False) or not tileType in game.tile.SOLID_TILES or (tileType == 23 and self.tiles[x][y].tileType == 0 and self.tiles[x][y].isActive) or (tileType == 2 and self.tiles[x][y].tileType == 0 and self.tiles[x][y].isActive) or (tileType == 60 and self.tiles[x][y].tileType == 59 and self.tiles[x][y].isActive) or (tileType == 70 and self.tiles[x][y].tileType == 59 and self.tiles[x][y].isActive):
      if (tile.tileType != 0 or not tile.isActive) and tileType in [2, 23]:
        return
      if (tile.tileType != 59 or not tile.isActive) and tileType == 60:
        return
      if tile.tileType == 81:
        if self.tiles[x - 1][y].isActive or self.tiles[x + 1][y].isActive or self.tiles[x][y - 1].isActive:
          return
        if not self.tiles[x][y + 1].isActive or not self.tiles[x][y + 1].isTileSolid():
          return
      if tile.liquid > 0 and tileType in [3, 4, 20, 24, 27, 32, 51, 69, 72]:
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
      elif tileType == 55 or tileType == 85:
        self.placeSign(x, y, tileType)
      elif tileType in game.tile.ALCHEMY_TILES:
        self.placeAlch(x, y, style)
      elif tileType == 79:
        direction = 1
        if plr > -1:
          direction = self.players[plr].direction
        self.place4x2(x, y, tileType, direction)
      elif tileType == 81:
        tile.frameX = 26 * random.randint(0, 6)
        tile.isActive = True
        tile.tileType = tileType
        self.tiles[x][y] = tile
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
        
  def closeDoor(self, x, y, forced = False):
    num = 0
    num2 = x
    num3 = y
    frameX = self.tiles[x][y].frameX
    frameY = self.tiles[x][y].frameY
    if frameX == 0:
      num = 1
    elif frameX == 18:
      num2 = x - 1
      num = 1
    elif frameX == 36:
      num2 = x + 1
      num = -1
    elif frameX == 54:
      num = -1
    if frameY == 18:
      num3 = y - 1
    elif frameY == 36:
      num3 = y - 2
    num4 = num2
    if num == -1:
      num4 = num2 - 1
    if not forced:
      for k in range(num3, num3 + 3):
        if not self.emptyTile(num2, k, True):
          return
    for l in range(num4, num4 + 2):
      for m in range(num3, num3 + 3):
        if l == num2:
          self.tiles[l][m] = self.tiles[l][m].copy()
          self.tiles[l][m].tileType = 10
          self.tiles[l][m].frameX = random.randint(0, 3) * 18
        else:
          self.tiles[l][m] = self.tiles[l][m].copy()
          self.tiles[l][m].isActive = False
    for n in range(num2 - 1, num2 + 1):
      for num5 in range(num3 - 1, num3 + 2):
        self.tileFrame(n, num5, False, False)
  
  def openDoor(self, x, y, direction):
    num = 0
    if self.tiles[x][y - 1].frameY == 0 and self.tiles[x][y - 1].tileType == self.tiles[x][y].tileType:
      num = y - 1
    elif self.tiles[x][y - 2].frameY == 0 and self.tiles[x][y - 2].tileType == self.tiles[x][y].tileType:
      num = y - 2
    elif self.tiles[x][y - 2].frameY == 0 and self.tiles[x][y + 1].tileType == self.tiles[x][y].tileType:
      num = y + 1
    else:
      num = y
    num2 = x
    num3 = 0
    num4 = 0
    if direction == -1:
      num2 = x - 1
      num3 = 36
      num4 = x - 1
    else:
      num2 = x
      num4 = x + 1
    flag = True
    for k in range(num, num + 3):
      if self.tiles[num4][k].isActive:
        if self.tiles[num4][k].tileType not in [3, 24, 52, 61, 62, 69, 71, 73, 74]:
          flag = False
          break
        self.killTile((num4, k), False, False, False)
    if flag:
      self.tiles[num2][ num] = self.tiles[num2][ num].copy()
      self.tiles[num2][ num].isActive = True
      self.tiles[num2][ num].tileType = 11
      self.tiles[num2][ num].frameY = 0
      self.tiles[num2][ num].frameX = num3
      self.tiles[num2 + 1][ num] = self.tiles[num2 + 1][ num].copy()
      self.tiles[num2 + 1][ num].isActive = True
      self.tiles[num2 + 1][ num].tileType = 11
      self.tiles[num2 + 1][ num].frameY = 0
      self.tiles[num2 + 1][ num].frameX = num3 + 18
      self.tiles[num2][ num + 1] = self.tiles[num2][ num + 1].copy()
      self.tiles[num2][ num + 1].isActive = True
      self.tiles[num2][ num + 1].tileType = 11
      self.tiles[num2][ num + 1].frameY = 18
      self.tiles[num2][ num + 1].frameX = num3
      self.tiles[num2 + 1][ num + 1] = self.tiles[num2 + 1][ num + 1].copy()
      self.tiles[num2 + 1][ num + 1].isActive = True
      self.tiles[num2 + 1][ num + 1].tileType = 11
      self.tiles[num2 + 1][ num + 1].frameY = 18
      self.tiles[num2 + 1][ num + 1].frameX = num3 + 18
      self.tiles[num2][ num + 2] = self.tiles[num2][ num + 2].copy()
      self.tiles[num2][ num + 2].isActive = True
      self.tiles[num2][ num + 2].tileType = 11
      self.tiles[num2][ num + 2].frameY = 36
      self.tiles[num2][ num + 2].frameX = num3
      self.tiles[num2 + 1][ num + 2] = self.tiles[num2 + 1][ num + 2].copy()
      self.tiles[num2 + 1][ num + 2].isActive = True
      self.tiles[num2 + 1][ num + 2].tileType = 11
      self.tiles[num2 + 1][ num + 2].frameY = 36
      self.tiles[num2 + 1][ num + 2].frameX = num3 + 18
      for l in range(num2 - 1, num2 + 2):
        for m in range(num - 1, num + 2):
          self.tileFrame(l, m, False, False)
    
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
