import logging
import struct

from world import World
from chest import Chest
from tile import Tile

log = logging.getLogger()

MAX_CHEST_ITEMS = 20

class WorldManager:

  def load(self, worldFile):
    if worldFile == None or len(worldFile) == 0:
      return None
    world = None
    try:
      world = self.__loadWorldFromFile(worldFile + '.wld')
    except Exception as ex:
      log.error(ex)
      print ex
    return world

  def __loadWorldFromFile(self, worldFile):
    f = open(worldFile, 'rb')
    # FIXME: write some sort of WorldReader class for all this stuff
    world = World()
    try:
      # first 4 bytes are the version
      fileVersion = struct.unpack('<i', f.read(4))[0]
      worldNameLen = struct.unpack('<B', f.read(1))[0]
      world.name = f.read(worldNameLen)
      log.debug("World name: " + world.name)
      world.worldId = struct.unpack('<i', f.read(4))[0]
      world.leftWorld = struct.unpack('<i', f.read(4))[0]
      world.rightWorld = struct.unpack('<i', f.read(4))[0]
      world.topWorld = struct.unpack('<i', f.read(4))[0]
      world.bottomWorld = struct.unpack('<i', f.read(4))[0]
      world.height = struct.unpack('<i', f.read(4))[0]
      world.width = struct.unpack('<i', f.read(4))[0]
      spawnTileX = struct.unpack('<i', f.read(4))[0]
      spawnTileY = struct.unpack('<i', f.read(4))[0]
      world.spawn = [spawnTileX, spawnTileY]
      world.worldSurface = struct.unpack('<d', f.read(8))[0]
      world.rockLayer = struct.unpack('<d', f.read(8))[0]
      world.time = struct.unpack('<d', f.read(8))[0]
      world.isDay = struct.unpack('<?', f.read(1))[0]
      world.moonphase = struct.unpack('<i', f.read(4))[0]
      world.isBloodMoon = struct.unpack('<?', f.read(1))[0]
      dungeonX = struct.unpack('<i', f.read(4))[0]
      dungeonY = struct.unpack('<i', f.read(4))[0]
      downedBoss1 = struct.unpack('<?', f.read(1))[0]
      downedBoss2 = struct.unpack('<?', f.read(1))[0]
      downedBoss3 = struct.unpack('<?', f.read(1))[0]
      shadowOrbSmashed = struct.unpack('<?', f.read(1))[0]
      spawnMeteor = struct.unpack('<?', f.read(1))[0]
      shadowOrbCount = struct.unpack('<B', f.read(1))[0]
      invasionDelay = struct.unpack('<i', f.read(4))[0]
      invasionSize = struct.unpack('<i', f.read(4))[0]
      invasionType = struct.unpack('<i', f.read(4))[0]
      invasionX = struct.unpack('<d', f.read(8))[0]
      self.readTiles(f, world)
      self.readChests(f, world)
      self.readSigns(f, world)
      log.debug("At file pos: " + str(f.tell()))
      self.readNPCs(f, world)
    finally:
      f.close()
    return world 

  def readNPCs(self, f, world):
    log.debug("Reading NPCs...")
    someFlag = struct.unpack('<?', f.read(1))[0]
    while someFlag:
      npcNameLen = struct.unpack('<B', f.read(1))[0]
      npcName = f.read(npcNameLen)
      npcX = struct.unpack('<f', f.read(4))[0]
      npcY = struct.unpack('<f', f.read(4))[0]
      homeless = struct.unpack('<?', f.read(1))[0]
      homeTileX = struct.unpack('<i', f.read(4))[0]
      homeTileY = struct.unpack('<i', f.read(4))[0]
      someFlag = struct.unpack('<?', f.read(1))[0]
 
  def readSigns(self, f, world):
    log.debug("reading signs...")
    for m in range(1000):
      tmp = struct.unpack('<?', f.read(1))[0]
      if tmp:
        signTextLen = struct.unpack('<B', f.read(1))[0]
        signText = f.read(signTextLen)
        num3 = struct.unpack('<i', f.read(4))[0]
        num4 = struct.unpack('<i', f.read(4))[0]
    
  def readTiles(self, f, world):
    log.debug("reading tiles...")
    log.debug("Width: " + str(world.width))
    log.debug("Height: " + str(world.height))
    empty = Tile()
    world.tiles = [[empty for y in range(world.height)] for x in range(world.width)]
    for x in range(world.width):
      for y in range(world.height):
        world.tiles[x][y].isActive = struct.unpack('<?', f.read(1))[0]
        if world.tiles[x][y].isActive:
          world.tiles[x][y].tileType = struct.unpack('<B', f.read(1))[0]
          if world.tiles[x][y].isImportant():
            world.tiles[x][y].frameX = struct.unpack('<h', f.read(2))[0]
            world.tiles[x][y].frameY = struct.unpack('<h', f.read(2))[0]
        world.tiles[x][y].isLighted = struct.unpack('<?', f.read(1))[0]
        tmp = struct.unpack('<?', f.read(1))[0]
        if tmp:
          world.tiles[x][y].wall = struct.unpack('<B', f.read(1))[0]
        tmp2 = struct.unpack('<?', f.read(1))[0]
        if tmp2:
          world.tiles[x][y].liquid = struct.unpack('<B', f.read(1))[0]
          world.tiles[x][y].isLava = struct.unpack('<?', f.read(1))[0]

  def readChests(self, f, world):
    log.debug("reading chests...")
    for k in range(1000):
      tmp1 = struct.unpack('<?', f.read(1))[0]
      if tmp1:
        chestX = struct.unpack('<i', f.read(4))[0]
        chestY = struct.unpack('<i', f.read(4))[0]
        for l in range(MAX_CHEST_ITEMS):
          chestItemStackSize = struct.unpack('<B', f.read(1))[0]
          if chestItemStackSize > 0:
            itemNameLen = struct.unpack('<B', f.read(1))[0]
            itemName = f.read(itemNameLen)
