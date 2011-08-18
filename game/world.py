import logging

from environment import SimulationTime

logger = logging.getLogger()

class World(SimulationTime):
  """
  Game world for Terraria. Handles things like daylight,
  bloodmoon, etc.
  """
  
  def __init__(self, granularity=16, platformClock=None, nightLength=32400, dayLength=52400):
    SimulationTime.__init__(self, granularity, platformClock)
    self.width = 1024 # maxTilesX
    self.height = 1024 # maxTilesY
    self.time = 0
    self.spawn = ()
    self.worldSurface = 0
    self.rockLayer = 0
    self.worldId = 0
    self.name = ""
    self.isDay = True
    self.nightLength = nightLength
    self.isBloodMoon = False
    self.moonPhase = 0
    self.dayLength = dayLength
    self.shadowOrbSmashed = False
    self.bossOneDowned = False
    self.bossTwoDowned = False
    self.bossThreeDowned = False
    self.leftWorld = 0
    self.rightWorld = 0
    self.bottomWorld = 0
    self.topWorld = 0
    self.version = 0
    self.dungeonX = 0
    self.dungeonY = 0
    self.spawnMeteor = False
    self.shadowOrbCount = 0
    self.invasionDelay = 0
    self.invasionSize = 0
    self.invasionType = 0
    self.invasionX = 0.0
	
  def _update(self, frames):
    SimulationTime._update(self, frames)
    self.time += 1.0
    if not self.isDay:
      if self.time > self.nightLength:
        # it should now turn to day time
        self.time = 0.0
        self.isDay = True
        self.isBloodMoon = False
    else:
      # its day time!
      if self.time > self.dayLength:
        self.time = 0.0
        self.isDay = False

  def getBossFlag(self):
    return 0
    
  def __repr__(self):
    return "<World('%s', '%dx%d')>" % (self.name, self.width, self.height)
