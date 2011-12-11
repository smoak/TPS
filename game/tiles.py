IMPORTANT_TILES = [3, 5, 10, 11, 12, 13, 14, 15, 16, 17, 18, 20, 21, 24, 26, 27, 28, 29, 31, 33, 34, 35, 36, 42, 50, 55, 61, 71, 72, 73, 74, 77, 78, 79, 81, 82, 83, 84, 85]


class TileSection(object):
  """
  A section of 200x150 tiles
  """

  def __init__(self):
    self.tiles = []
    self.x = 0 # the x section
    self.y = 0 # the y section

  def getTileAt(self, coord):
    """
    Gets a tile at a specified x, y coordinate
    Formula is: y * width + x
    Width = 200 (always?)
    """
    if len(self.tiles) > 0 and coord[0] > 0 and coord[1] > 0 and (coord[1] * 200 + coord[0]) < len(self.tiles):
      return self.tiles[coord[1] * 200 + coord[0]]
    return None

class TileFlags:
  Active = 1
  Light = 2
  Wall = 4
  Liquid = 8

class Tile(object):
  """
  """
  
  def __init__(self):
    self.tileType = 0
    self.frameX = -1
    self.frameY = -1
    self.x = 0
    self.y = 0
    self.wall = -1
    self.isLava = False
    self.liquid = -1
    self.active = False
    self.isLighted = False

  def getFlags(self):
    flag = 0
    if self.active:
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
