import copy

class TileType:
  Dirt = 0
  Stone = 1
  Grass = 2
  Iron = 6
  Copper = 7
  Gold = 8
  Silver = 9 
  Meteorite = 37
  Sand = 53
    

class TileFlags:
  Active = 1
  Light = 2
  Wall = 4
  Liquid = 8

IMPORTANT_TILES = [3, 5, 10, 11, 12, 13, 14, 15, 16, 17, 18, 20, 21, 24, 26, 27, 28, 29, 31, 33, 34, 35, 36, 42, 50, 55, 61, 71, 72, 73, 74, 77, 78, 79, 81, 82, 83, 84, 85]
STONE_TILES = [63, 64, 65, 66, 67, 68]
SOLID_TILES = [0, 1, 2, 6, 7, 8, 9, 10, 19, 22, 23, 25, 30, 37, 38, 39, 40, 41, 43, 44, 45, 46, 47, 48, 53, 54, 56, 57, 58, 59, 60, 63, 64, 65, 66, 67, 68, 70, 75, 76]
NO_ATTACH_TILES = [3, 4, 10, 13, 14, 15, 16, 17, 18, 19, 20, 21, 27, 50]
TABLE_TILES = [14, 18, 19]
SOLID_TOP_TILES = [14, 16, 18, 19]
ALCHEMY_TILES = [ 82, 83, 84 ]


class Tile(object):
  __slots__ = ["tileType", "isActive", "frameX", "frameY", "wall", "isLava", "isLighted", "liquid", "frameNumber", "checkingLiquid"]
  def __init__(self):
    self.tileType = 0
    self.isActive = False
    self.frameX = 0
    self.frameY = 0
    self.wall = 0
    self.isLava = False
    self.isLighted = False
    self.liquid = 0
    self.frameNumber = 0
    self.checkingLiquid = False

  def copy(self):
    return copy.copy(self) 

  def getFlags(self):
    flag = 0
    if self.isActive:
      flag = flag | TileFlags.Active
    if self.isLighted:
      flag = flag | TileFlags.Light
    if self.wall > 0:
      flag = flag | TileFlags.Wall
    if self.liquid > 0:
      flag = flag | TileFlags.Liquid
    return flag

  def isImportant(self):
    return self.tileType in IMPORTANT_TILES

  def isTileStone(self):
    return self.tileType in STONE_TILES

  def isTileSolid(self):
    return self.tileType in SOLID_TILES
    
  def isTileTable(self):
    return self.tileType in TABLE_TILES
    
  def isTileSolidTop(self):
    return self.tileType in SOLID_TOP_TILES


class AirTile(Tile):
  """
  This isnt really a tile...
  """
  def __init__(self):
    Tile.__init__(self)
    self.tileType = 0
    self.isActive = False
    self.isLighted = True
    self.frameX = 0
    self.frameY = 0
    self.wall = 0
    self.isLava = False
    self.liquid = 0

class DirtTile(Tile):
  """
  Dirt tile. Most mineable tiles will subclass this
  """
  def __init__(self):
    Tile.__init__(self)
    self.tileType = TileType.Dirt
    self.isActive = True
    self.isLighted = True
    self.frameX = -1
    self.frameY = -1

class StoneTile(DirtTile):
  def __init__(self):
    DirtTile.__init__(self)
    self.tileType = TileType.Stone
