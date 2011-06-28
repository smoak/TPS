from net.message import MessageType
from message import BaseMessage

class RequestPlayerDataMessage(BaseMessage):
  def __init__(self):
    self._messageType = MessageType.RequestPlayerData
	  self.clientNumber = -1
    
  def serialize(self):
    pass