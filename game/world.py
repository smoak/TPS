from environment import SimulationTime

class World(SimulationTime):
  """
  Game world for Terraria. Handles things like daylight,
  bloodmoon, etc.
  """
  
  def __init__(self, granularity=16, platformClock=None):
    SimulationTime.__init__(self, granularity, platformClock)
	  self.width = 1024 # maxTilesX
	  self.height = 1024 # maxTilesY
	