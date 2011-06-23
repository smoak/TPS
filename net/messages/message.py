import struct

class Message(object):
  messageTypeFormat = "<B"
  messageTypeFormatLen = struct.calcsize(messageTypeFormat)

  def __init__(self):
    self.messageLen = 0
    self.messageType = -1

  def serialize(self):
    pass

  def deserialize(self):
    pass

  def getMessageTypeFromString(self, message):
    """
    Gets the message type from the bytearray string
    """
    return struct.unpack(self.messageTypeFormat, message[0:self.messageTypeFormatLen])[0]
