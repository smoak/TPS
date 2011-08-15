import logging

from twisted.internet import reactor
from twisted.internet.endpoints import serverFromString

from factories import TerrariaFactory


logger = logging.getLogger()

class TerrariaServer:
  """
  The main server that handles everything
  """
 
  def __init__(self, config, world):
    self.config = config
    self.world = world
    self.factory = TerrariaFactory(world, config)
    serverEndpoint = "tcp:%d:interface=%s" % (self.config.listenPort, self.config.listenAddress)
    self.endpoint = serverFromString(reactor, serverEndpoint)

  def run(self):
    logger.debug("Starting Server")
    self.endpoint.listen(self.factory)
    logger.debug("Listening. %s:%d" % (self.config.listenAddress, self.config.listenPort))
    reactor.run()