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