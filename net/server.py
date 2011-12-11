import logging

from twisted.internet import reactor
from twisted.internet.endpoints import serverFromString

from factories import TerrariaFactory
from game.world import World
from game.tiles import TileSection, Tile


logger = logging.getLogger()


def tmpDebugWorldRemoveMe():
  # THIS IS FOR DEBUG ONLY!!
  w = World(platformClock=reactor)
  w.time = 13500.0
  w.name = "Debug"
  w.width = 800
  w.height = 600
  w.spawn = (100,199)
  w.isDay = True
  w.worldSurface = 200
  w.rockLayer = 400
  t = Tile()
  t.active = True
  t.tileType = 0
  for x in range(10):
    w.tileSections.append([])
    for y in range(10):
      ts = TileSection()
      ts.x = x
      ts.y = y
      if y > 0:
        for ty in range(150):
          for tx in range(200):
            ts.tiles.append(t)
      w.tileSections[x].append(ts)
  return w

class TerrariaServer:
  """
  The main server that handles everything
  """
 
  def __init__(self, config):
    self.config = config
    self.world = tmpDebugWorldRemoveMe()
    self.factory = TerrariaFactory(self.world, config)
    serverEndpoint = "tcp:%d:interface=%s" % (self.config.listenPort, self.config.listenAddress)
    self.endpoint = serverFromString(reactor, serverEndpoint)

  def run(self):
    logger.debug("Starting Server")
    self.endpoint.listen(self.factory)
    logger.debug("Listening. %s:%d" % (self.config.listenAddress, self.config.listenPort))
    self.world.start()
    reactor.run()
