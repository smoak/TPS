import logging
import struct

from world import World
from chest import Chest

log = logging.getLogger()

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

  def __isImportant(self, tileType):
    return tileType in [3, 5, 10, 11, 12, 13, 14, 15, 16, 17, 18, 20, 21, 24, 26, 27, 28, 29, 31, 33, 34, 35, 36, 42, 50, 55, 61, 71, 72, 73, 74, 77, 78, 79]

  def __loadWorldFromFile(self, worldFile):
    f = open(worldFile, 'rb')
    # FIXME: write some sort of WorldReader class for all this stuff
    world = World()
    try:
      # first 4 bytes are the version
      fileVersion = struct.unpack('<i', f.read(4))[0]
      worldNameLen = struct.unpack('<B', f.read(1))[0]
      worldName = f.read(worldNameLen)
      log.debug("World name: " + worldName)
      worldId = struct.unpack('<i', f.read(4))[0]
      leftWorld = struct.unpack('<i', f.read(4))[0]
      rightWorld = struct.unpack('<i', f.read(4))[0]
      topWorld = struct.unpack('<i', f.read(4))[0]
      bottomWorld = struct.unpack('<i', f.read(4))[0]
      maxTilesY = struct.unpack('<i', f.read(4))[0]
      maxTilesX = struct.unpack('<i', f.read(4))[0]
      spawnTileX = struct.unpack('<i', f.read(4))[0]
      spawnTileY = struct.unpack('<i', f.read(4))[0]
      worldSurface = struct.unpack('<d', f.read(8))[0]
      rockLayer = struct.unpack('<d', f.read(8))[0]
      tempTime = struct.unpack('<d', f.read(8))[0]
      tempDayTime = struct.unpack('<?', f.read(1))[0]
      tempMoonPhase = struct.unpack('<i', f.read(4))[0]
      tempBloodMoon = struct.unpack('<?', f.read(1))[0]
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
      self.readTiles(f, world, maxTilesX, maxTilesY)
      self.readChests(f, world)
      self.readSigns(f, world)
      someFlag = struct.unpack('<?', f.read(1))[0]
      while someFlag:
        npcNameLen = struct.unpack('<B', f.read(1))[0]
        npcName = f.read(npcNameLen)
        npcX = struct.unpack('<f', f.read(4))[0]
        npcY = struct.unpack('<f', f.read(4))[0]
        homeless = struct.unpack('<?', f.read(1))[0]
        homeTileX = struct.unpack('<i', f.read(4))[0]
        homeTileY = struct.unpack('<i', f.read(4))[0]
        someFlag = struct.unpack('<?', f.read(1))
    finally:
      f.close()
    return world 
 
  def readSigns(self, f, world):
    log.debug("reading signs...")
    for m in range(1000):
      tmp = struct.unpack('<?', f.read(1))[0]
      if tmp:
        signTextLen = struct.unpack('<B', f.read(1))[0]
        signText = f.read(signTextLen)
        num3 = struct.unpack('<i', f.read(4))[0]
        num4 = struct.unpack('<i', f.read(4))[0]
    
  def readTiles(self, f, world, maxTilesX, maxTilesY):
    log.debug("reading tiles...")
    for x in range(maxTilesX):
      for y in range(maxTilesY):
        active = struct.unpack('<?', f.read(1))[0]
        if active:
          tileType = struct.unpack('<B', f.read(1))[0]
          if self.__isImportant(tileType):
            frameX = struct.unpack('<h', f.read(2))[0]
            frameY = struct.unpack('<h', f.read(2))[0]
          else:
            frameX = -1
            frameY = -1
        lighted = struct.unpack('<?', f.read(1))[0]
        tmp = struct.unpack('<?', f.read(1))[0]
        if tmp:
          wall = struct.unpack('<B', f.read(1))[0]
        tmp2 = struct.unpack('<?', f.read(1))[0]
        if tmp2:
          liquid = struct.unpack('<B', f.read(1))[0]
          lava = struct.unpack('<?', f.read(1))[0]

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
            itemName = f.read(iteamNameLen)
