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
    
  def __sendDisconnect(self, connection, text):
    message = Message(MessageType.Disconnect)
    message.appendRaw(text)
    connection.socket.send(message.create())

  def __processConnectionRequest(self, message, connection):
    clientVersion = message.buf[1:]
    if clientVersion != server.SERVER_VERSION:
      log.warn("Unsupported client version. Got: " + str(clientVersion))
      self.__sendDisconnect(connection, "Unsupported client version.")
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
    if not self.__checkClientIdFor(message, connection):
      return
    # byte 0
    # byte 1 is the slot of the item
    # byte 2 is the stack size
    # rest is item name
    clientNum = struct.unpack('<B', message.buf[1])[0]
    itemData = struct.unpack('<BB', message.buf[2:4])
    slot = itemData[0]
    amount = itemData[1]
    itemName = message.buf[4:]
    if slot < 44:
      # its an inventory item
      connection.player.inventory.setSlot(slot, itemName, amount)
    else:
      # its some type of armor
      connection.player.armor.setSlot(slot - 44, itemName, amount)
    
    if clientNum == 255:
      # Send the item to other clients because its a server generated item?
      log.warn("Implement sending item data to other clients when clientNum == 255")

  def __processRequestWorldDataMessage(self, message, connection):
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
    log.warn("Need to implement Sending item info...")
#    for i in range(200):
#      itemInfoMsg = Message(MessageType.ItemInfo)
#      item = self.server.world.items[i]
#      itemInfoMsg.appendInt(i)
#      itemInfoMsg.appendFloat(
#      itemOwnerInfoMsg = Message(MessageType.ItemOwnerInfo)

  def __sendNpcInfo(self, connection):
    log.warn("Need to implement Sending NPC info...")

  def __processTileBlockRequestMessage(self, message, connection):
    x,y = struct.unpack('<ii', message.buf[1:9])
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
    # msgType, remoteClient, ignoreClient, text, number, number2, number3, number4
    # NetMessage.SendData(25, plr, -1, "Welcome to " + Main.worldName + "!", 255, 255f, 240f, 20f);
    message = Message(MessageType.Message)
    message.appendByte(255) # who sent the message? 255 means server sent message
    message.appendByte(255) # R 
    message.appendByte(0) # G
    message.appendByte(0) # B
    message.appendRaw("Welcome to the jungle! We got fun and games!")
    log.debug("Sending motd to " + connection.player.name)
    connection.socket.send(message.create())

  def __sendPlayerUpdateTwoMessageFor(self, connection):
    playerUpdateTwoMsg = Message(MessageType.PlayerUpdateTwo)
    playerUpdateTwoMsg.appendByte(connection.clientNumber)
    playerUpdateTwoMsg.appendByte(True)
    self.__sendMessageToOtherClients(playerUpdateTwoMsg, connection)
	
  def __sendPlayerUpdateOneMessageFor(self, connection):
    playerUpdateOneMessage = Message(MessageType.PlayerUpdateOne)
    playerUpdateOneMessage.appendByte(connection.clientNumber)
    playerUpdateOneMessage.appendByte(connection.player.playerFlags)
    playerUpdateOneMessage.appendByte(connection.player.selectedItem)
    playerUpdateOneMessage.appendFloat(connection.player.posX)
    playerUpdateOneMessage.appendFloat(connection.player.posY)
    playerUpdateOneMessage.appendFloat(connection.player.velX)
    playerUpdateOneMessage.appendFloat(connection.player.velY)
    self.__sendMessageToOtherClients(playerUpdateOneMessage, connection)

  def __sendPlayerHealthUpdateMessageFor(self, connection):
    playerHealthUpdateMessage = Message(MessageType.PlayerHealthUpdate)
    playerHealthUpdateMessage.appendByte(connection.clientNumber)
    playerHealthUpdateMessage.appendInt16(connection.player.statLife)
    playerHealthUpdateMessage.appendInt16(connection.player.statLifeMax)
    self.__sendMessageToOtherClients(playerHealthUpdateMessage, connection)
	
  def __sendPvpModeMessageFor(self, connection):
    pvpModeMessage = Message(MessageType.PvpMode)
    pvpModeMessage.appendByte(connection.clientNumber)
    pvpModeMessage.appendByte(False)
    self.__sendMessageToOtherClients(pvpModeMessage, connection)
	
  def __sendPlayerManaUpdateMessageFor(self, connection):
    manaUpdateMessage = Message(MessageType.PlayerManaUpdate)
    manaUpdateMessage.appendByte(connection.clientNumber)
    manaUpdateMessage.appendInt(connection.player.mana)
    manaUpdateMessage.appendInt(connection.player.manaMax)
    self.__sendMessageToOtherClients(manaUpdateMessage, connection)
	
  def __sendPlayerDataMessageFor(self, connection):
    playerData = Message(MessageType.PlayerData)
    playerData.appendByte(connection.clientNumber)
    playerData.appendByte(connection.player.hairStyle)
    # FIXME: theres got to be a better way to do this...
    for i in range(3):
      playerData.appendByte(connection.player.hairColor[i])
    for i in range(3):
      playerData.appendByte(connection.player.skinColor[i])
    for i in range(3):
      playerData.appendByte(connection.player.eyeColor[i])
    for i in range(3):
      playerData.appendByte(connection.player.shirtColor[i])
    for i in range(3):
      playerData.appendByte(connection.player.underShirtColor[i])
    for i in range(3):
      playerData.appendByte(connection.player.pantsColor[i])
    for i in range(3):
      playerData.appendByte(connection.player.shoeColor[i])
    playerData.appendRaw(connection.player.name)
    self.__sendMessageToOtherClients(playerData, connection)

  def __sendInventoryFor(self, connection):
    # send inventory items
    i = 0
    for item in connection.player.inventory.items:   
      itemMessage = Message(MessageType.InventoryData)
      itemMessage.appendByte(connection.clientNumber)
      itemMessage.appendByte(i)
      itemMessage.appendByte(item.stackSize)
      itemMessage.appendRaw(item.itemName)
      self.__sendMessageToOtherClients(itemMessage, connection)
      i += 1
      
    # send armor
    for armor in connection.player.armor.items:
      itemMessage = Message(MessageType.InventoryData)
      itemMessage.appendByte(connection.clientNumber)
      itemMessage.appendByte(i)
      itemMessage.appendByte(armor.stackSize)
      itemMessage.appendRaw(armor.itemName)
      self.__sendMessageToOtherClients(itemMessage, connection)
      i += 1
    
  def __sendRawMessageToOtherClients(self, message, clientToIgnore):
    cons = self.connectionManager.getConnectionList()
    for c in cons:
      if c.authed and c.clientNumber != clientToIgnore.clientNumber:
        c.socket.send(message)

  def __sendPvpTeamMessageFor(self, connection):
    pvpTeamMessage = Message(MessageType.PvpTeam)
    pvpTeamMessage.appendByte(connection.clientNumber)
    pvpTeamMessage.appendByte(0) # TODO: implement pvp mode
    self.__sendMessageToOtherClients(pvpTeamMessage, connection)
	
  def __syncPlayers(self, connection):
    log.debug("Syncing players")
    cons = self.connectionManager.getConnectionList()
    for ci in cons:
      self.__sendPlayerUpdateTwoMessageFor(ci)
      self.__sendPlayerUpdateOneMessageFor(ci)
      self.__sendPlayerHealthUpdateMessageFor(ci)
      self.__sendPvpModeMessageFor(ci)
      self.__sendPvpTeamMessageFor(ci)
      self.__sendPlayerManaUpdateMessageFor(ci)
      self.__sendPlayerDataMessageFor(ci)
      self.__sendInventoryFor(ci)

  def __processSpawnMessage(self, message, connection):
    spawnX, spawnY = struct.unpack('<ii', message.buf[1:9])
    connection.player.spawn = (spawnX, spawnY)
    # we have to send spawn data to the other clients and NOT this one...
    response = Message(MessageType.Spawn)
    response.appendInt(connection.clientNumber)
    response.appendInt(spawnX)
    response.appendInt(spawnY)
    self.__sendMessageToOtherClients(response, connection)
    self.__greetPlayer(connection)
    self.__syncPlayers(connection)

  def __sendMessageToOtherClients(self, message, clientToIgnore):
    cons = self.connectionManager.getConnectionList()
    for c in cons:
      if c.authed and c.clientNumber != clientToIgnore.clientNumber:
        c.socket.send(message.create())

  def __processPlayerHealthUpdateMessage(self, message, connection):
    if not self.__checkClientIdFor(message, connection):
      return
    connection.player.statLife, connection.player.statMaxLife = struct.unpack('<hh', message.buf[1:5])
    if connection.player.statLife <= 0:
      connection.player.dead = True
    self.__sendPlayerHealthUpdateMessageFor(connection)

  def __processPlayerManaUpdateMessage(self, message, connection):
    if not self.__checkClientIdFor(message, connection):
      return
    clientNumber = message.buf[1]
    connection.player.mana, connection.player.manaMax = struct.unpack('<hh', message.buf[1:5])
    self.__sendPlayerManaUpdateMessageFor(connection)

  def __processSendSpawnMessage(self, message, connection):
    log.warning("need to implement got send spawn message")

  def __processPlayerUpdateOneMessage(self, message, connection):
    if not self.__checkClientIdFor(message, connection):
      return
    num = struct.unpack('<B', message.buf[1])[0]
    connection.player.playerFlags = struct.unpack('<B', message.buf[2])[0]
    connection.player.selectedItem = struct.unpack('<B', message.buf[3])[0]
    connection.player.posX,connection.player.posY = struct.unpack('<ff', message.buf[4:12])
    connection.player.velX,connection.player.velY = struct.unpack('<ff', message.buf[12:20])
    response = Message(MessageType.PlayerUpdateTwo)
    response.appendByte(num)
    response.appendByte(connection.player.playerFlags)
    response.appendByte(connection.player.selectedItem)
    response.appendFloat(connection.player.posX)
    response.appendFloat(connection.player.posY)
    response.appendFloat(connection.player.velX)
    response.appendFloat(connection.player.velY)
    self.__sendMessageToOtherClients(response, connection)

  def __processZoneInfoMessage(self, message, connection):
    log.debug("Got ZoneInfoMessage")

  def __processNpcTalkMessage(self, message, connection):
    log.debug("Got NpcTalkMessage")
    
  def __processManipulateTileMessage(self, message, connection):
    log.debug("Got ManipulateTileMessage")
    num4 = message.buf[1]
    x, y = struct.unpack('<ii', message.buf[2:10])
    flag = struct.unpack('<?', message.buf[10])[0]
    if not flag:
      if num4 == 0 or num4 == 2:
        pass
      elif num4 == 1 or num4 == 3:
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
    elif message.messageType == MessageType.ManipulateTile:
      self.__processManipulateTileMessage(message, connection)
    else:
      log.warning("Need to implement message type: " + str(message.messageType))
