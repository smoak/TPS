from twisted.internet.protocol import ServerFactory

from protocols import TerrariaProtocol
from parsers import BinaryMessageParser
from handlers import MessageHandlerLocator

class TerrariaFactory(ServerFactory):
  """
  Server factory used to create protocols.

  @ivar world: The L{World} which will be served by protocols created by this factory
  """
  def __init__(self, world, config):
    self.world = world
    self.config = config
    self.parser = BinaryMessageParser()
    self.messageHandlerLocator = MessageHandlerLocator()
    self.clients = []

  def buildProtocol(self, ignored):
    p = TerrariaProtocol(self.parser, self.messageHandlerLocator, self.world, self.config)
    p.factory = self
    self.clients.append(p)
    return p
    
  def sendMessageToOtherClients(self, message, proto):
    for p in self.clients:
      if p != proto:
        p.sendMessage(message)
        
  def sendMessageToAllClients(self, message):
    for p in self.clients:
      p.sendMessage(message)
