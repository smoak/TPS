import struct
import logging

from message import Message, MessageType
import server
from game.player import Player
from util.math import *


CONNECTION_REQUEST_FORMAT = '<s' # Little Endian 
log = logging.getLogger()

class MessageHandlerService:

  def __init__(self, server):
    self.connectionManager = server.connectionManager
    self.server = server

  def __processConnectionRequest(self, message, connection):
    log.debug("Got connection request")
    clientVersion = message.buf[1:]
    if clientVersion != server.SERVER_VERSION:
      log.debug("Unsupported client version. Got: " + str(clientVersion))
      self.connectionManager.removeConnection(connection)
      return

    response = None
    if self.server.password != None:
      response = Message(MessageType.PasswordRequest)
    else:
      response = Message(MessageType.RequestPlayerData)
      response.appendInt(connection.clientNumber)
    connection.authed = True
    connection.socket.send(response.create())

  def __checkClientIdFor(self, message, connection):
    clientId = struct.unpack('<B', message.buf[1])[0] # client id    
    return self.__ensureCorrectClientId(clientId, connection)

  def __processPlayerDataMessage(self, message, connection):
    log.debug("got player data message")
    # index 0 is message type...
    if not self.__checkClientIdFor(message, connection):
      return
    connection.player = Player()
    connection.player.hairStyle = struct.unpack('<B', message.buf[2])[0]
    # FIXME: There's probably a better way to do this...for now this works...
    colors = []
    # get all color info:
    for i in range(3, 22, 3):    
      colors.append(struct.unpack('<BBB', message.buf[i:i+3]))
    connection.player.hairColor = colors[0]
    connection.player.skinColor = colors[1]
    connection.player.eyeColor = colors[2]
    connection.player.shirtColor = colors[3]
    connection.player.underShirtColor = colors[4]
    connection.player.pantsColor = colors[5]
    connection.player.shoeColor = colors[6]

    # player name is the remaining bytes (starting at index 24)
    connection.player.name = message.buf[24:]
    log.debug("Player " + connection.player.name + " has connected!")

  def __ensureCorrectClientId(self, clientIdRecvd, connection):
    result = True
    if not self.__validClientId(clientIdRecvd, connection):
      log.warning("client id mismatch")
      log.warning("received: " + str(clientIdRecvd) + " actual: " + str(connection.clientNumber))
      self.connectionManager.removeConnection(connection)
      result = False
    return result  

  def __validClientId(self, clientIdSent, connection):
    return clientIdSent == connection.clientNumber

  def __processInventoryDataMessage(self, message, connection):
    log.debug("Got inventory data message")
    if not self.__checkClientIdFor(message, connection):
      return
    # byte 0
    # byte 1 is the slot of the item
    # byte 2 is the stack size
    # rest is item name
    itemData = struct.unpack('<BB', message.buf[1:3])
    slot = itemData[0]
    amount = itemData[1]
    itemName = message.buf[3:]
    connection.player.inventory.setSlot(slot, itemName, amount)

  def __processRequestWorldDataMessage(self, message, connection):
    log.debug("Got world data message")
    world = self.server.world
    response = Message(MessageType.WorldData)
    try:
      response.appendInt(world.time)
      response.appendByte(world.isDay)
      response.appendByte(world.moonphase)
      response.appendByte(world.isBloodMoon)

      response.appendInt(world.width) # maxTilesX
      response.appendInt(world.height) # maxTilesY

      spawn = world.spawn
      response.appendInt(spawn[0])
      response.appendInt(spawn[1])
    
      response.appendInt(world.dirtLayer)
      response.appendInt(world.rockLayer)

      # NOTE: This is 0 because Terraria saves the world id
      # incorrectly (e.g. 610775162) so we just send 0...
      response.appendByte(0) # World Id

      response.appendRaw(world.name)
      connection.socket.send(response.create())
    except Exception as ex:
      log.error(ex)

  def __processTileBlockRequestMessage(message, connection):
    log.debug("Got tile block request")
    

  def processMessage(self, message, connection):
    if not connection.authed and message.messageType != MessageType.ConnectionRequest and message.messageType != MessageType.PasswordResponse:
      log.debug("Connection not authed!")
      self.connectionManager.removeConnection(connection)
      return      
    if message.messageType == MessageType.ConnectionRequest:
      self.__processConnectionRequest(message, connection)
    elif message.messageType == MessageType.PlayerData:
      self.__processPlayerDataMessage(message, connection)
    elif message.messageType == MessageType.InventoryData:
      self.__processInventoryDataMessage(message, connection)
    elif message.messageType == MessageType.RequestWorldData:
      self.__processRequestWorldDataMessage(message, connection)
    elif message.messageType == MessageType.TileBlockRequest:
      self.__processTileBlockRequestMessage(message, connection)
