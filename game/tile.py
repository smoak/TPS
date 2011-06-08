class TileType:
  Air = 0
  Dirt = 1  

class TileFlags:
  Active = 1
  Light = 2
  Wall = 4
  Liquid = 8

IMPORTANT_TILES = [3, 5, 10, 11, 12, 13, 14, 15, 16, 17, 18, 20, 21, 24, 26, 27, 28, 29, 31, 33, 34, 35, 36, 42, 50, 55, 61, 71, 72, 73, 74, 77, 78, 79]

class Tile(object):
  __slots__ = ["tileType", "isActive", "frameX", "frameY", "wall", "isLava", "isLighted", "liquid"]
  def __init__(self):
    self.tileType = 0
    self.isActive = False
    self.frameX = 0
    self.frameY = 0
    self.wall = 0
    self.isLava = False
    self.isLighted = False
    self.liquid = 0

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

  @classmethod
  def isImportant(cls, tileType):
    return tileType in IMPORTANT_TILES
