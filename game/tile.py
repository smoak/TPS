class TileType:
  AIR = 0
  DIRT = 1  

class TileFlags:
  ACTIVE = 1
  LIGHT = 2
  WALL = 4
  LIQUID = 8

IMPORTANT_TILES = [3, 5, 10, 11, 12, 13, 14, 15, 16, 17, 18, 20, 21, 24, 26, 27, 28, 29, 31, 33, 34, 35, 36, 42, 50, 55, 61, 71, 72, 73, 74, 77, 78, 79]

class Tile:
  def __init__(self):
    self.tileType = 0
    self.isActive = False
    self.frameX = 0
    self.frameY = 0
    self.wall = 0
    self.isLava = False
    self.isLighted = False
    self.liquid = 0

  @classmethod
  def isImportant(cls, tileType):
    return tileType in IMPORTANT_TILES
