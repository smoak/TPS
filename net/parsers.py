from struct import calcsize, unpack
import logging

from messages import ConnectionRequestMessage, PlayerInfoMessage, PlayerHpMessage, PlayerManaMessage, PlayerBuffMessage

logger = logging.getLogger()

def parseConnectionRequest(rawMessage, session):
  message = ConnectionRequestMessage()
  message.clientVersion = rawMessage
  return message

messageLookup = {
  ConnectionRequestMessage.MESSAGE_TYPE: parseConnectionRequest,
  PlayerInfoMessage.MESSAGE_TYPE: (lambda m, s: PlayerInfoMessage(s).deserialize(m)),
  PlayerHpMessage.MESSAGE_TYPE: (lambda m, s: PlayerHpMessage(s).deserialize(m)),
  PlayerManaMessage.MESSAGE_TYPE: (lambda m, s: PlayerManaMessage(s).deserialize(m)),
  PlayerBuffMessage.MESSAGE_TYPE: (lambda m, s: PlayerBuffMessage(s).deserialize(m))
}

class BinaryMessageParser(object):
  """
  A class to parse binary messages into higher level
  messages.
  """
  messageTypeFormat = "<B"
  messageTypeFormatLen = calcsize(messageTypeFormat)

  def parse(self, message, session=None):
    """
    Parses the binary message into a higher level message
    
    @param message: bytearray starting with messageType
    """
    #logger.debug("Parsing raw message: %r" % (message,))
    messageStr = str(message)
    pos = 0
    messageType, = unpack(self.messageTypeFormat, messageStr[pos:self.messageTypeFormatLen])
    pos += self.messageTypeFormatLen
    # dont include message type...
    return messageLookup[messageType](messageStr[1:], session)   
