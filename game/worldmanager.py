import logging
import struct

from world import World

log = logging.getLogger()

class WorldMananger:

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
    return tileType in [3, 21, 28]

  def __loadWorldFromFile(self, worldFile):
    f = open(worldFile, 'rb')
    # FIXME: write some sort of WorldReader class for all this stuff
    world = World()
    try:
      # first 4 bytes are the version
      fileVersion = struct.unpack('<i', f.read(4))[0]
      worldNameLen = struct.unpack('<B', f.read(1))[0]
      worldName = f.read(worldNameLen)
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
    finally:
     f.close()
    return None 
    
     
