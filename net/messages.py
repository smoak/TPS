from struct import calcsize, pack, unpack
import logging

from net.handlers import MessageHandlerLocator
from game.player import Player

logger = logging.getLogger()

class Message(object):
  """
  Base message class for Terraria messages
  """

  headerFormat = "<i"
  headerFormatLen = calcsize(headerFormat)
  int16Format = "<h"
  int16FormatLen = calcsize(int16Format)
  int32Format = "<i"
  int32FormatLen = calcsize(int32Format)
  floatFormat = "<f"
  floatFormatLen = calcsize(floatFormat)
  byteFormat = "<B"
  byteFormatLen = calcsize(byteFormat)
  messageTypeFormat = "<B"
  messageTypeFormatLen = calcsize(messageTypeFormat)
  boolFormat = "<?"
  boolFormatLen = calcsize(boolFormat)
  color24Format = "<BBB"
  color24FormatLen = calcsize(color24Format)

  def __init__(self, messageType):
    self.messageType = messageType
    self._messageLen = 0
    self._messageBuf = bytearray()
    self._currentPos = 0

  def serialize(self):
    """
    Convert me into a wire-encoded bytearray
    """
    messageLen = len(self._messageBuf) + 1 # 1 byte for the message type
    header = pack(self.headerFormat, messageLen)
    msgType = pack(self.messageTypeFormat, self.messageType)
    payload = str(self._messageBuf)
    return header + msgType + payload

  def handler(cls, methodfunc):
    MessageHandlerLocator.handlerLookup[cls] = methodfunc
    logger.debug(MessageHandlerLocator.handlerLookup)
    return methodfunc
  handler = classmethod(handler)
  
  def deserialize(self, rawBinaryData):
    self._messageLen, = unpack(self.headerFormat, rawBinaryData[self._currentPos:self._currentPos + self.headerFormatLen])
    self._currentPos += self.headerFormatLen

  def __writeValue(self, valFormat, val):
    """
    Writes a value with a specific format into internal message buffer
    """
    self._messageBuf.extend(pack(valFormat, val))

  def _writeByte(self, val):
    """
    Writes a byte value into the internal message buffer
    """
    self.__writeValue(self.byteFormat, val)

  def _writeInt32(self, val):
    """
    Writes a 32 bit signed integer into the internal message buffer
    """
    self.__writeValue(self.int32Format, val)

  def _writeBool(self, val):
    """
    Writes a boolean value into the internal message buffer
    """
    self.__writeValue(self.boolFormat, val)
    
  def _readByte(self, rawData, offset=0):
    """
    Reads a byte from rawData starting at offset
    """
    val, = unpack(self.byteFormat, rawData[offset:offset + self.byteFormatLen])
    return val
    
  def _readBool(self, rawData, offset=0):
    """
    Reads a boolean from rawData starting at offset
    """
    val, = unpack(self.boolFormat, rawData[offset:offset + self.boolFormatLen])
    return val
    
  def _readColor24(self, rawData, offset=0):
    """
    Reads a color24 from rawData starting at offset
    """
    return unpack(self.color24Format, rawData[offset:offset+self.color24FormatLen])

  def _readInt16(self, rawData, offset=0):
    """
    Reads a 16 bit signed integer (i.e. short) from rawData starting at offset
    """    
    val, = unpack(self.int16Format, rawData[offset:offset+self.int16FormatLen])
    return val

  def _readInt32(self, rawData, offset=0):
    """
    Reads a 32 bit signed integer from rawData starting at offset
    """
    val, = unpack(self.int32Format, rawData[offset:offset+self.int32FormatLen])
    return val
 
class ConnectionRequestMessage(Message):
  """
  Represents a connection request message
  """

  MESSAGE_TYPE = 0x01  

  def __init__(self):
    Message.__init__(self, self.MESSAGE_TYPE)
    self.clientVersion = ""

  def serialize(self):
    self._messageBuf = bytearray()
    self._messageBuf.extend(self.clientVersion)
    return Message.serialize(self)

  def __repr__(self):
    return repr(self.serialize())

class DisconnectMessage(Message):
  """
  A message to disconnect the client with a reason (text)
  """

  MESSAGE_TYPE = 0x02

  def __init__(self):
    Message.__init__(self, self.MESSAGE_TYPE)
    self.text = ""

  def serialize(self):
    self._messageBuf = bytearray()
    self._messageBuf.extend(self.text)
    return Message.serialize(self)

  def __repr__(self):
    return repr(self.serialize())

class PasswordRequestMessage(Message):
  """
  A message to request a password from the client
  """

  MESSAGE_TYPE = 0x25

  def __init__(self):
    Message.__init__(self, self.MESSAGE_TYPE)
  
class RequestPlayerDataMessage(Message):
  """
  A message to request that the client sends
  the player data
  """

  MESSAGE_TYPE = 0x03

  def __init__(self):
    Message.__init__(self, self.MESSAGE_TYPE)
    self.clientNumber = None
    
class PlayerMessage(Message):
  """
  Represents common player messages
  """
  
  def __init__(self, messageType, session):
    Message.__init__(self, messageType)
    self.player = session.player
    if self.player is None:
      self.player = Player()
    
  def deserialize(self, rawData):
    self.player.playerId = self._readByte(rawData, self._currentPos)
    self._currentPos += self.byteFormatLen
    return self
    
class PlayerInfoMessage(PlayerMessage):
  """
  Contains player data such as name, hair color,
  skin color, etc.
  """
  
  MESSAGE_TYPE = 0x04

  def __init__(self, session):
    PlayerMessage.__init__(self, self.MESSAGE_TYPE, session)
    self.playerId = None
    self.hair = None
    self.isMale = False
    
  def deserialize(self, rawBinaryData):
    """
    Turns a wire encoded (i.e. binary) object into a PlayerInfoMessage object
    """
    PlayerMessage.deserialize(self, rawBinaryData)
    self.player.hair = self._readByte(rawBinaryData, self._currentPos)
    self._currentPos += self.byteFormatLen
    self.player.isMale = self._readBool(rawBinaryData, self._currentPos)
    self._currentPos += self.boolFormatLen
    self.player.hairColor = self._readColor24(rawBinaryData, self._currentPos)
    self._currentPos += self.color24FormatLen
    self.player.skinColor = self._readColor24(rawBinaryData, self._currentPos)
    self._currentPos += self.color24FormatLen
    self.player.eyeColor = self._readColor24(rawBinaryData, self._currentPos)
    self._currentPos += self.color24FormatLen
    self.player.shirtColor = self._readColor24(rawBinaryData, self._currentPos)
    self._currentPos += self.color24FormatLen
    self.player.underShirtColor = self._readColor24(rawBinaryData, self._currentPos)
    self._currentPos += self.color24FormatLen
    self.player.pantsColor = self._readColor24(rawBinaryData, self._currentPos)
    self._currentPos += self.color24FormatLen
    self.player.shoeColor = self._readColor24(rawBinaryData, self._currentPos)
    self._currentPos += self.color24FormatLen
    self.player.difficulty = self._readByte(rawBinaryData, self._currentPos)
    self._currentPos += self.byteFormatLen
    self.player.name = rawBinaryData[self._currentPos:]
    self._currentPos += len(self.player.name)
    return self
    
class PlayerHpMessage(PlayerMessage):
  """
  Player hp info
  """
  
  MESSAGE_TYPE = 0x10
  
  def __init__(self, session):
    PlayerMessage.__init__(self, self.MESSAGE_TYPE, session)
    
  def deserialize(self, rawData):
    PlayerMessage.deserialize(self, rawData)
    self.player.life = self._readInt16(rawData, self._currentPos)
    self._currentPos += self.int16FormatLen
    self.player.lifeMax = self._readInt16(rawData, self._currentPos)
    self._currentPos += self.int16FormatLen
    return self
    
class PlayerManaMessage(PlayerMessage):
  """
  Mana info for a player.
  
  MessageType: 0x2A (42)
  
  Message Format:
  Byte: Id of player
  Short: Mana
  Short: Max Mana
  """
  
  MESSAGE_TYPE = 0x2A # 42
  
  def __init__(self, session):
    PlayerMessage.__init__(self, self.MESSAGE_TYPE, session)
    
  def deserialize(self, rawData):
    PlayerMessage.deserialize(self, rawData)
    self.player.mana = self._readInt16(rawData, self._currentPos)
    self._currentPos += self.int16FormatLen
    self.player.manaMax = self._readInt16(rawData, self._currentPos)
    self._currentPos += self.int16FormatLen
    return self
    
class PlayerBuffMessage(PlayerMessage):
  """
  Player buff message.
  
  MessageType: 0x32 (50)
  
  Message Format:
  Byte: Id of player
  Byte: Buff type for buff slot 0
  Byte: Buff type for buff slot 1
  Byte: Buff type for buff slot 2
  Byte: Buff type for buff slot 3
  Byte: Buff type for buff slot 4
  Byte: Buff type for buff slot 5
  Byte: Buff type for buff slot 6
  Byte: Buff type for buff slot 7
  Byte: Buff type for buff slot 8
  Byte: Buff type for buff slot 9
  """
  
  MESSAGE_TYPE = 0x32
  
  def __init__(self, session):
    PlayerMessage.__init__(self, self.MESSAGE_TYPE, session)
    
  def deserialize(self, rawData):
    PlayerMessage.deserialize(self, rawData)
    # TODO
    return self
    
class PlayerInventoryMessage(PlayerMessage):
  """
  Message concerning player inventory
  
  MessageType: 0x05
  
  MessageFormat:
  Byte: Id of player
  Byte: Slot number of item
  Byte: Stack size of item
  String: Name of item
  """
  
  MESSAGE_TYPE = 0x05
  
  def __init__(self, session):
    PlayerMessage.__init__(self, self.MESSAGE_TYPE, session)
    
  def deserialize(self, rawData):
    PlayerMessage.deserialize(self, rawData)
    # TODO
    return self

class RequestWorldDataMessage(Message):
  """
  The client sends this message after sending all player info. It doesnt contain any other data though...
  """

  MESSAGE_TYPE = 0x06

  def __init__(self):
    Message.__init__(self, self.MESSAGE_TYPE)

  def deserialize(self, rawData):
    # nothing to deserialize...
    return self


class WorldDataMessage(Message):
  """
  Sent to the client in response to a L{RequestWorldDataMessage}

  MessageType: 0x07

  MessageFormat:
  int32: world time
  bool: is day time
  byte: moon phase
  bool: blood moon?
  int32: world width (maxTilesX)
  int32: world height (maxTilesY)
  int32: spawn X
  int32: spawn Y
  int32: world surface
  int32: rock layer
  int32: world id
  byte: boss flag (1 = shadow orb smashed, 2 = downed boss 1, 4 = downed boss 2, 8 = downed boss 3)
  string: world name
  """
  
  MESSAGE_TYPE = 0x07

  def __init__(self):
    Message.__init__(self, self.MESSAGE_TYPE)
    self.world = None

  def serialize(self):
    """
    Serializes this instance into a binary format
    """
    self._messageBuf = bytearray()
    self._writeInt32(self.world.time)
    self._writeBool(self.world.isDay)
    self._writeByte(self.world.moonPhase)
    self._writeBool(self.world.isBloodMoon)
    self._writeInt32(self.world.width)
    self._writeInt32(self.world.height)
    self._writeInt32(self.world.spawn[0])
    self._writeInt32(self.world.spawn[1])
    self._writeInt32(self.world.worldSurface)
    self._writeInt32(self.world.rockLayer)
    self._writeInt32(self.world.worldId)
    self._writeByte(self.world.getBossFlag())
    # write the raw name
    self._messageBuf.extend(self.world.name)
    return Message.serialize(self)

class TileBlockRequestMessage(Message):
  """
  Sent from client to request a section of tiles

  MessageType: 0x08

  MessageFormat:
  int32: tile x
  int32: tile y
  """

  MESSAGE_TYPE = 0x08

  def __init__(self):
    Message.__init__(self, self.MESSAGE_TYPE)
    self.tileX = -1
    self.tileY = -1

  def deserialize(self, rawData):
    self.tileX = self._readInt32(rawData, self._currentPos)
    self._currentPos += self.int32FormatLen
    self.tileY = self._readInt32(rawData, self._currentPos)
    self._currentPos += self.int32FormatLen
    return self

class TileLoadingMessage(Message):
  """
  Tells the client tiles are about to be sent

  MessageType: 0x09

  MessageFormat:
  int32: some unknown number
  string: always 'Receiving tile data'
  """

  MESSAGE_TYPE = 0x09

  def __init__(self):
    Message.__init__(self, self.MESSAGE_TYPE)
    self.text = "Receiving tile data"
    self.unknownNumber = 0

  def serialize(self):
    self._messageBuf = bytearray()
    self._writeInt32(self.unknownNumber)
    self._messageBuf.extend(self.text)
    return Message.serialize(self)
