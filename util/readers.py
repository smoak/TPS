from struct import calcsize, unpack

from game.world import World

byteOrder = "<"
int32Format = byteOrder + "i"
int32FormatLen = calcsize(int32Format)
ucharFormat = byteOrder + "B"
ucharFormatLen = calcsize(ucharFormat)
doubleFormat = byteOrder + "d"
doubleFormatLen = calcsize(doubleFormat)
boolFormat = byteOrder + "?"
boolFormatLen = calcsize(boolFormat)

class TerrariaFileReader(object):
  """
  Base object for reading various Terraria files
  """
  
  fileHandle = None
  
  def _read(self, format, formatLen):
    """
    Reads binary data from a file and advances filePos
    """
    val, = unpack(format, self.fileHandle.read(formatLen))
    return val
    
  def readInt32(self):
    return self._read(int32Format, int32FormatLen)
    
  def readUChar(self):
    return self._read(ucharFormat, ucharFormatLen)
    
  def readDouble(self):
    return self._read(doubleFormat, doubleFormatLen)
    
  def readBoolean(self):
    return self._read(boolFormat, boolFormatLen)

class WorldFileReader(TerrariaFileReader):
  """
  Reads a L{World} object from a file.
  """
  
  def __init__(self, worldFilePath):
    self.worldFilePath = worldFilePath
    
  def readWorld(self):
    w = World()
    self.fileHandle = open(self.worldFilePath, 'rb')
    w.version = self.readInt32()
    worldNameLen = self.readUChar()
    w.name = self.fileHandle.read(worldNameLen)
    w.worldId = self.readInt32()
    w.leftWorld = self.readInt32()
    w.rightWorld = self.readInt32()
    w.topWorld = self.readInt32()
    w.bottomWorld = self.readInt32()
    w.height = self.readInt32()
    w.width = self.readInt32()
    spawnX = self.readInt32()
    spawnY = self.readInt32()
    w.spawn = (spawnX, spawnY)
    w.worldSurface = self.readDouble()
    w.rockLayer = self.readDouble()
    w.time = self.readDouble()
    w.isDay = self.readBoolean()
    w.moonPhase = self.readInt32()
    w.isBloodMoon = self.readBoolean()
    w.dungeonX = self.readInt32()
    w.dungeonY = self.readInt32()
    w.bossOneDowned = self.readBoolean()
    w.bossTwoDowned = self.readBoolean()
    w.bossThreeDowned = self.readBoolean()
    w.shadowOrbSmashed = self.readBoolean()
    w.spawnMeteor = self.readBoolean()
    w.shadowOrbCount = self.readUChar()
    w.invasionDelay = self.readInt32()
    w.invasionSize = self.readInt32()
    w.invasionType = self.readInt32()
    w.invasionX = self.readDouble()
    self.fileHandle.close()
    return w