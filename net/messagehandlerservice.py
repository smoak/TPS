import struct
import logging

from messagetype import MessageType
from message import Message
import server


CONNECTION_REQUEST_FORMAT = '<s' # Little Endian 
log = logging.getLogger("MessageHandlerService")

class MessageHandlerService:

  def __init__(self, connectionManager):
    self.connectionManager = connectionManager

  def __processConnectionRequest(self, message, connection):
    print server.ByteToHex(message.buf)
    clientVersion = message.buf[1:]
    print "Got clientVersion: " + clientVersion
    if clientVersion != server.SERVER_VERSION:
      self.connectionManager.removeConnection(connection)
      return
    response = Message(MessageType.RequestPlayerData)
    response.appendInt(connection.clientNumber)
    print "sending message to client " + str(connection.clientNumber)
    connection.socket.send(response.create())
    print "sent " + server.ByteToHex(response.create())

  def processMessage(self, message, connection):
    print "in processMessage"
    if not connection.authed and message.messageType != MessageType.ConnectionRequest and message.messageType != MessageType.PasswordResponse:
      self.connectionManager.removeConnection(connection)
      return      
    if message.messageType == MessageType.ConnectionRequest:
      self.__processConnectionRequest(message, connection)
