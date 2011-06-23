import struct

from net.message import MessageType
from messages import *

class MessageParser(object):
  messageTypeFormat = "<B"
  messageTypeFormatLen = struct.calcsize(messageTypeFormat)
  messages = { MessageType.ConnectionRequest: connectionrequest.ConnectionRequest() }

  def parse(self, message):
    """
    Parses a message into a higher level protobuf class
    @param message string of bytes starting with the msgType
    """
    msgType, = struct.unpack(self.messageTypeFormat, message[0:self.messageTypeFormatLen])
    if not self.messages.has_key(msgType):
      # handle unknown or unsupported messageType
      print "handle unknown/unsupported message"
      return None
    message = message[self.messageTypeFormatLen:]
    return self.messages[msgType].deserialize(message)
    
