import struct
import logging

from message import Message, MessageType
import server
from game.player import Player


CONNECTION_REQUEST_FORMAT = '<s' # Little Endian 
log = logging.getLogger("MessageHandlerService")

class MessageHandlerService:

  def __init__(self, server):
    self.connectionManager = server.connectionManager
    self.server = server

  def __processConnectionRequest(self, message, connection):
    clientVersion = message.buf[1:]
    if clientVersion != server.SERVER_VERSION:
      self.connectionManager.removeConnection(connection)
      return

    response = None
    if self.server.password != None:
      response = Message(MessageType.PasswordRequest)
    else:
      response = Message(MessageType.RequestPlayerData)
      response.appendInt(connection.clientNumber)
    connection.socket.send(response.create())

  def __processPlayerDataMessage(self, message, connection):
    clientId = message.buf[0] # client id    
    if not self.__ensureCorrectClientId(clientId, connection):
      return
    connection.player = Player()

  def __ensureCorrectClientId(self, clientIdRecvd, connection):
    result = True
    if not self.__validClientId(clientIdRecvd, connection):
      log.warning("client id mismatch")
      self.connectionManager.removeConnection(connection)
      result = False
    return result  

  def __validClientId(self, clientIdSent, connection):
    return clientIdSent == connection.clientNumber

  def processMessage(self, message, connection):
    if not connection.authed and message.messageType != MessageType.ConnectionRequest and message.messageType != MessageType.PasswordResponse:
      self.connectionManager.removeConnection(connection)
      return      
    if message.messageType == MessageType.ConnectionRequest:
      self.__processConnectionRequest(message, connection)
    elif message.messageType == MessageType.PlayerData:
      self.__processPlayerDataMessage(message, connection)
