import struct
import logging

from message import Message, MessageType
import server
from game.player import Player
from util.math import *
from game.tile import *


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
    
      response.appendInt(world.worldSurface)
      response.appendInt(world.rockLayer)

      # NOTE: This is 0 because Terraria saves the world id
      # incorrectly (e.g. 610775162) so we just send 0...
      response.appendByte(0) # World Id

      response.appendRaw(world.name)
      connection.socket.send(response.create())
    except Exception as ex:
      log.error(ex)
  
  def __sendSection(self, coords, connection):
    sectionX = coords[0]
    sectionY = coords[1]
    world = self.server.world
    maxSectionsX = world.width / 200
    maxSectionsY = world.height / 150
    if sectionX >= 0 and sectionY >= 0 and sectionX < maxSectionsX and sectionY < maxSectionsY:
      toSectionX = sectionX * 200
      toSectionY = sectionY * 150
      for i in range(toSectionY, toSectionY + 150):
        tileSectionMsg = Message(MessageType.TileSection)
        tileSectionMsg.appendInt16(200) 
        tileSectionMsg.appendInt(toSectionX)
        tileSectionMsg.appendInt(i)
        for j in range(toSectionX, (200 + toSectionX)):
          tile = world.tiles[j][i]
          tileSectionMsg.appendByte(tile.getFlags())
          
          if tile.isActive:
            tileSectionMsg.appendByte(tile.tileType)
            # append important stuff
            if Tile.isImportant(tile.tileType):
              tileSectionMsg.appendInt16(tile.frameX)
              tileSectionMsg.appendInt16(tile.frameY)
          if tile.wall > 0:
            tileSectionMsg.appendByte(tile.wall)
          if tile.liquid > 0:
            tileSectionMsg.appendByte(tile.liquid)
            tileSectionMsg.appendByte(tile.isLava)
        connection.socket.send(tileSectionMsg.create())  

  def __sendItemInfo(self, connection):
    log.debug("Sending item info...")
#    for i in range(200):
#      itemInfoMsg = Message(MessageType.ItemInfo)
#      item = self.server.world.items[i]
#      itemInfoMsg.appendInt(i)
#      itemInfoMsg.appendFloat(
#      itemOwnerInfoMsg = Message(MessageType.ItemOwnerInfo)
    

  def __sendNpcInfo(self, connection):
    log.debug("Sending NPC info...")
    

  def __processTileBlockRequestMessage(self, message, connection):
    log.debug("Got tile block request")
    x,y = struct.unpack('<ii', message.buf[1:9])
    log.debug("Requesting tile: (" + str(x) + ", " + str(y) + ")")
    flag = True
    if x == -1 or y == -1:
      flag = False
    else:
      if x < 10 or x > self.server.world.width - 10:
        flag = False 
      elif y < 10 or y > self.server.world.height - 10:
        flag = False
    num7 = 1350
    if flag:
      num7 = num7 * 2
    response = Message(MessageType.TileLoading)
    response.appendInt(num7)
    response.appendRaw("Receiving tile data")
    connection.socket.send(response.create())
    sectionX = self.server.world.getSectionX(self.server.world.spawn[0])
    sectionY = self.server.world.getSectionY(self.server.world.spawn[1])
    log.debug("(sectionX, sectionY): (" + str(sectionX) + ", " + str(sectionY) + ")")
    for j in range(sectionX - 2, sectionX + 3):
      for k in range(sectionY - 1, sectionY + 2):
        self.__sendSection((j, k), connection)
    if flag:
      x = self.server.world.getSectionX(x)
      y = self.server.world.getSectionY(y)
      for j in range(x - 2, x + 3):
        for k in range(y - 1, y + 2):
          self.__sendSection((j,k), connection)
      tileConfirm = Message(MessageType.TileConfirmed)
      tileConfirm.appendInt(x - 2)
      tileConfirm.appendInt(y - 1)
      tileConfirm.appendInt(x + 2)
      tileConfirm.appendInt(y + 1)
      connection.socket.send(tileConfirm.create())
    # More tiles...
    tileConfirm = Message(MessageType.TileConfirmed)
    tileConfirm.appendInt(sectionX - 2)
    tileConfirm.appendInt(sectionY - 1)
    tileConfirm.appendInt(sectionX + 2)
    tileConfirm.appendInt(sectionY + 1)
    connection.socket.send(tileConfirm.create())
    # Now ask for spawn info
    response = Message(MessageType.SendSpawn)
    connection.socket.send(response.create())
    # Now send item info
    self.__sendItemInfo(connection)
    self.__sendNpcInfo(connection)

  def __greetPlayer(self, connection):
    message = Message(MessageType.Message)
    message.appendByte(255)
    message.appendByte(255)
    message.appendByte(240)
    message.appendByte(20)
    message.appendRaw("TEST MESSAGE!")
    connection.socket.send(message.create())

  def __syncPlayers(self, connection):
    pass

  def __processSpawnMessage(self, message, connection):
    log.debug("Processing spawn message")
    spawnX, spawnY = struct.unpack('<ii', message.buf[1:9])
    connection.player.spawn = (spawnX, spawnY)
    # we have to send spawn data to the other clients and NOT this one...
  #  response = Message(MessageType.Spawn)
  #  response.appendInt(connection.clientNumber)
  #  response.appendInt(spawnX)
  #  response.appendInt(spawnY)
  #  log.debug("Sending " + connection.player.name + "'s spawn info to other connected clients")
    self.__greetPlayer(connection)
 #   self.__sendMessageToOtherClients(response, connection)

  def __sendMessageToOtherClients(self, message, clientToIgnore):
    cons = self.connectionManager.getConnectionList()
    for c in cons:
      if c.authed and c.clientNumber != clientToIgnore.clientNumber:
        c.socket.send(message.create())

  def __processPlayerHealthUpdateMessage(self, message, connection):
    log.debug("got player health update message")

  def __processPlayerManaUpdateMessage(self, message, connection):
    log.debug("got player mana update message")

  def __processSendSpawnMessage(self, message, connection):
    log.debug("got send spawn message")

  def __processPlayerUpdateOneMessage(self, message, connection):
    log.debug("got player update one message")
    if not self.__checkClientIdFor(message, connection):
      return
    num = struct.unpack('<B', message.buf[1])[0]
    playerFlags = struct.unpack('<B', message.buf[2])[0]
    selectedItem = struct.unpack('<B', message.buf[3])[0]
    posX,posY = struct.unpack('<ff', message.buf[4:12])
    velX,velY = struct.unpack('<ff', message.buf[12:20])
    response = Message(MessageType.PlayerUpdateTwo)
    response.appendByte(num)
    response.appendByte(playerFlags)
    response.appendByte(selectedItem)
    response.appendFloat(posX)
    response.appendFloat(posY)
    response.appendFloat(velX)
    response.appendFloat(velY)
    self.__sendMessageToOtherClients(response, connection)

  def __processZoneInfoMessage(self, message, connection):
    pass

  def __processNpcTalkMessage(self, message, connection):
    pass

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
    elif message.messageType == MessageType.Spawn:
      self.__processSpawnMessage(message, connection)
    elif message.messageType == MessageType.PlayerHealthUpdate:
      self.__processPlayerHealthUpdateMessage(message, connection)
    elif message.messageType == MessageType.PlayerManaUpdate:
      self.__processPlayerManaUpdateMessage(message, connection)
    elif message.messageType == MessageType.SendSpawn:
      self.__processSendSpawnMessage(message, connection)
    elif message.messageType == MessageType.PlayerUpdateOne:
      self.__processPlayerUpdateOneMessage(message, connection)
    elif message.messageType == MessageType.ZoneInfo:
      self.__processZoneInfoMessage(message, connection)
    elif message.messageType == MessageType.NpcTalk:
      self.__processNpcTalkMessage(message, connection)
    else:
      log.warning("Need to implement message type: " + str(message.messageType))
