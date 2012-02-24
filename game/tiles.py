IMPORTANT_TILES = [3, 5, 10, 11, 12, 13, 14, 15, 16, 17, 18, 20, 21, 24, 26, 27, 28, 29, 31, 33, 34, 35, 36, 42, 50, 55, 61, 71, 72, 73, 74, 77, 78, 79, 81, 82, 83, 84, 85]
SECTION_WIDTH = 200
SECTION_HEIGHT = 150

class TileFlags:
  Active = 1
  Light = 2
  Wall = 4
  Liquid = 8


class TileType:
  """
  Enum for all the tile types
  """
  Air = -1
  Dirt = 0
  Stone = 1

class Tile:
  """
  The basic building blocks of life!
  """
  
  def __init__(self, tileType=TileType.Air, frameX=-1, frameY=-1, wall=-1, liquid=-1, isLava=False, isLighted=False, active=False):
    self.tileType = tileType
    self.frameX = frameX
    self.frameY = frameY
    self.wall = wall
    self.isLava = isLava
    self.liquid = liquid
    self.isLighted = isLighted
    self.active = active
    #self.x = -1
    #self.y = -1

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

airTile = Tile(TileType.Air,isLighted=True,frameX=0,frameY=0,wall=0,liquid=0)
dirtTile = Tile(TileType.Dirt, isLighted=True, wall=0, liquid=0, active=True)

class TileSection:
  """
  A section of 200x150 tiles
  """

  def __init__(self):
    self.allocated = False
    self.tiles = None
    self.x = -1 # the x section
    self.y = -1 # the y section
    self.worldWidth = 0
    self.tileType = -1

  def setTile(self, x, y, tile):
    """
    Sets a tile at the given coordinate within this section.
    Coordinate should be relative to the section and NOT the world
  
    Example: 10, 10 would mean row 10 column 10 of this section.
    The tile's x and y would be offset from the section
    """
#    tile.x = self.x * SECTION_WIDTH + x
#    tile.y = self.y * SECTION_HEIGHT + y
    if self.allocated:
      self.tiles[y * SECTION_WIDTH + x] = tile
    elif tile.tileType != self.tileType:
      self.allocated = True
      self.tiles = []
      for i in range(SECTION_WIDTH * SECTION_HEIGHT):
        self.tiles.append(airTile)
      self.tiles[y * SECTION_WIDTH + x] = tile
    
    

  def getTileAt(self, coord):
    """
    Gets a tile at a specified x, y coordinate
    Formula is: y * width + x
    Width = 200 (always?)
    """
    if len(self.tiles) > 0 and coord[0] > 0 and coord[1] > 0 and (coord[1] * 200 + coord[0]) < len(self.tiles):
      return self.tiles[coord[1] * SECTION_WIDTH + coord[0]]
    return None
