from net.message import MessageType
#from net.messages.message import *
from message import Message

class ConnectionRequest(Message):
  def __init__(self):
    Message.__init__(self)
    self.clientVersion = ""
    self.messageType = MessageType.ConnectionRequest

  def serialize(self):
    msg = bytearray(struct.pack(self.messageTypeFormat, self.messageType))
    msg.extend(self.clientVersion)

  def deserialize(self, message):
    self.clientVersion = message
    return self
  
