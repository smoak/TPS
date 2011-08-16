import struct, logging, time

from zope.interface import Interface, implements
from twisted.internet.error import ConnectionLost, ConnectionClosed
from twisted.internet.defer import Deferred, maybeDeferred, fail
from twisted.internet.protocol import Protocol
from twisted.python.failure import Failure
from twisted.internet.threads import deferToThread


from messages import ConnectionRequestMessage, DisconnectMessage, RequestPlayerDataMessage, PlayerInfoMessage, PlayerHpMessage, PlayerManaMessage, PlayerBuffMessage, PlayerInventoryMessage, RequestWorldDataMessage, WorldDataMessage, TileBlockRequestMessage, TileLoadingMessage
from resources.strings import Strings


logger = logging.getLogger()


UNHANDLED_ERROR_CODE = 'UNHANDLED'

class IMessageSender(Interface):
  """
  A transport which can send L{Message} objects.
  """

  def sendMessage(message):
    """
    Send a L{Message}

    @raise ConnectionLost if the underlying connection
    has already been lost.
    """

class IMessageReceiver(Interface):
  """
  An application object which can receive L{Message} objects
  and dispatch them appropriately
  """

  def startReceivingMessages(messageSender):
    """
    The L{messageReceived} method will start being called; messages 
    may be responded to by responding to the given L{IMessageSender}.

    @param messageSender: an L{IMessageSender} provider.
    """

  def messageReceived(message):
    """
    A message was received from the transport; dispath it appropriately
    """

  def stopReceivingMessages(reason):
    """
    No further messages will be received on this connection
 
    @param reason: L{Failure}
    """
    
class IMessageHandler(Interface):
  """
  An application object which can handle L{Message} objects
  """
  
  def handleConnectionRequest(message):
    """
    Handles a new connection request message
    """

class ProtocolManager:
  """
  Class to manage all connected protocols
  """

  def __init__(self):
    self.protocols = []

  def connectionMade(self, proto):
    """
    Invoked by a protocol when a connection is made.
    This will add the protocol to the list of protocols
    """
    self.protocols.append(proto)

  def connectionLost(self, proto):
    """
    Invoked by a protocol when the connection is lost.
    This will remove the protocol from the list of protocols
    """
    self.protocols.remove(proto)

  def sendMessageToAllProtocols(self, message):
    """
    Sends a message to all connected protocols
    """
    for p in self.protocols:
      p.sendMessage(message)

  def sendMessageToAllOtherProtocols(self, message, ignoredProtocols):
    """
    Sends a message to all protocols that are not in the ignoredProtocols list
    """
    for p in self.protocols:
      if p not in ignoredProtocols:
        p.sendMessage(message)

class MessageHandler:
  """
  """
  implements(IMessageHandler)

class MessageError(Exception):
  """
  Base class of all Message related exceptions
  """

class RemoteMessageError(MessageError):
  """
  This error indicates that something went wrong on the remote end of
  the connection, and the error was serialized and transmitted to you.
  """

  def __init__(self, errorCode, description, fatal=False, local=None):
    if local:
      localwhat = ' (local)'
      othertb = local.getBriefTraceback()
    else:
      localwhat = ''
      othertb = ''
    Exception.__init__(self, "Code<%s>%s: %s%s" % (
            errorCode, localwhat, description, othertb))
    self.local = local
    self.errorCode = errorCode
    self.description = description
    self.fatal = fatal

class UnhandledMessage(MessageError):
  """
  A message received could not be dispatched.
  """

class MessageDispatcher:
  """
    
  """
  implements(IMessageReceiver)

  def __init__(self, messageHandlerLocator):
    self.messageHandlerLocator = messageHandlerLocator

  def startReceivingMessages(self, messageSender):
    self.messageSender = messageSender

  def messageReceived(self, message):
    self._dispatchMessage(message)

  def stopReceivingMessages(self, reason):
    logger.debug("Stopping")

  def _dispatchMessage(self, message):
    """
    A message was received.
  
    Dispatch it to a local handler call it.
    """
    logger.debug("Dispatching message")
  #  logger.debug(message)
    handler = self.messageHandlerLocator.locateHandler(message)
    if handler is None:
      return fail(RemoteMessageError(
              UNHANDLED_ERROR_CODE,
              "Unhandled Message: %r" % (message,),
              False,
              local=Failure(UnhandledMessage())))
    return handler


class BinaryMessageProtocol(Protocol):
  """
  The binary message protocol of Terraria
  """

  implements(IMessageSender)

  headerFormat = "<I"
  headerFormatLen = struct.calcsize(headerFormat)
  MAX_LENGTH = 9999

  def __init__(self, messageParser, messageReceiver):
    self.messageReceiver = messageReceiver
    self.messageParser = messageParser

  def sendMessage(self, message):
    logger.debug("Sending message %s" % (message))
    logger.debug(self.address)
    self.transport.write(message.serialize())

  def connectionMade(self):
    self._messageBuffer = bytearray()
    self.messageReceiver.startReceivingMessages(self)
    logger.debug("Connection made")
    
  def connectionLost(self, reason):
    # tell the protocol manager the connection was lost
    self.protocolManager.connectionLost(self)
    #self.sendServerMessage(Strings.PlayerDisconnectedFormat % (self.player.name))

  def dataReceived(self, data):
    """
    Called whenever data is received
    """
    self._messageBuffer.extend(data)
    while len(self._messageBuffer) >= self.headerFormatLen:
      length ,= struct.unpack(self.headerFormat, str(self._messageBuffer[:self.headerFormatLen]))
      if length > self.MAX_LENGTH:
        self.lengthLimitExceeded(length)
        break
      if len(self._messageBuffer) < length + self.headerFormatLen:
        break
      messageRaw = self._messageBuffer[self.headerFormatLen:length + self.headerFormatLen]
      #logger.debug("Got raw message %s" % (repr(messageRaw)))
      self._messageBuffer = self._messageBuffer[length + self.headerFormatLen:]
      message = self.messageParser.parse(messageRaw, self)
      self.messageReceived(message)

  def lengthLimitExceeded(self, length):
    """
    Callback invoked when a length prefix greater than C{MAX_LENGTH} is
    received. The default implementation disconnects the transport.

    @param length: The length prefix which was received.
    @type length: C{int}
    """
    # TODO: handle this better
    self.transport.loseConnection()

class TerrariaSession(object):
  """
  Represents a players session.
  Holds data such as the player object,
  their client number, if they have been
  authed or not, etc.
  """

  def sessionConnect(self, address):
    """
    Initializes a new session
    """
    self.address = address
    self.player = None
    self.clientNumber = TerrariaSession.getNextAvailableClientNumber()
    self.isAuthed = False

  lastClientNumber = -1
  def getNextAvailableClientNumber(cls):
    return cls.lastClientNumber + 1

  getNextAvailableClientNumber = classmethod(getNextAvailableClientNumber)
    
PROTOCOL_VERSION = "Terraria20"
class TerrariaProtocol(BinaryMessageProtocol, MessageDispatcher, TerrariaSession, MessageHandler):
  """
  Base protocol for reading messages from Terraria
  """


  def __init__(self, messageParser, messageHandlerLocator, world, config, protocolManager, messageReceiver=None):
    if messageReceiver is None:
      messageReceiver = self
    messageHandlerLocator.messageHandler = self
    MessageDispatcher.__init__(self, messageHandlerLocator)
    BinaryMessageProtocol.__init__(self, messageParser, messageReceiver)
    self.world = world
    self.config = config
    self.protocolManager = protocolManager

  def connectionMade(self):
    """
    Called when a connection is first established
    """
    # tell the protocol manager that a new connection has arrived
    self.protocolManager.connectionMade(self)
    self.sessionConnect(self.transport.client)
    logger.debug("New connection with client number %d" % (self.clientNumber))
    BinaryMessageProtocol.connectionMade(self)

  def _disconnect(self, reason=None):
    if reason:
      message = DisconnectMessage()
      message.text = reason
      self.sendMessage(message)
    self.transport.loseConnection()
    self.protocolManager.connectionLost(self)

  def handleConnectionRequest(self, message):
    logger.debug("Got connection request message")
    if message.clientVersion != PROTOCOL_VERSION:
      self._disconnect(Strings.UnsupportedClientVersion)    
      return
    response = None
    if self.config.serverPassword != "":
      response = PasswordRequestMessage()
    else:
      response = RequestPlayerDataMessage()
      response.clientNumber = self.clientNumber
      self.isAuthed = True
    self.sendMessage(response)

  ConnectionRequestMessage.handler(handleConnectionRequest)
  
  def newPlayer(self, playerInfoMessage):
    self.player = playerInfoMessage.player
    logger.debug("%s has joined!" % (self.player.name))
    
  PlayerInfoMessage.handler(newPlayer)
  
  def gotPlayerHp(self, playerHpMessage):
    logger.debug("Got player hp")
     
  PlayerHpMessage.handler(gotPlayerHp)
  
  def gotPlayerMana(self, playerManaMessage):
    logger.debug("Got player mana")
    
  PlayerManaMessage.handler(gotPlayerMana)
  
  def gotPlayerBuff(self, playerBuffMessage):
    logger.debug("Player buff")
    
  PlayerBuffMessage.handler(gotPlayerBuff)

  def gotPlayerInventory(self, playerInventoryMessage):
    logger.debug("Player inventory")

  PlayerInventoryMessage.handler(gotPlayerInventory)

  def gotWorldRequest(self, worldDataMessage):
    m = WorldDataMessage()
    m.world = self.world
    self.sendMessage(m)
  
  RequestWorldDataMessage.handler(gotWorldRequest)

  def gotTileBlockRequest(self, tileBlockRequestMessage):
    flag3 = True
    x = tileBlockRequestMessage.tileX
    y = tileBlockRequestMessage.tileY
    if x == -1 or y == -1:
      flag3 = False
    elif x < 10 or x > self.world.width - 10:
      flag3 = False
    elif y < 10 or y > self.world.height - 10:
      flag3 = False
    someNumber = 1350 # not quite sure what this is yet
    if flag3:
      someNumber *= 2
    tileLoading = TileLoadingMessage()
    # not quite sure what this is for yet
    tileLoading.unknownNumber = someNumber
    self.sendMessage(tileLoading)
    # ask for spawn info
    response = SendSpawnMessage()
    self.sendMessage(response)

  TileBlockRequestMessage.handler(gotTileBlockRequest)
