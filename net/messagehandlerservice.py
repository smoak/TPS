import struct
import logging, re

from message import Message, MessageType
import server
from game.player import Player
from util.math import *
from game.tile import *
from net.messagesender import *
from service.itemservice import ItemService


CONNECTION_REQUEST_FORMAT = '<s' # Little Endian 
log = logging.getLogger()

class MessageHandlerService:

  def __init__(self, server):
    self.connectionManager = server.connectionManager
    self.server = server
    self.messageSender = MessageSender(self.connectionManager)
    self.itemService = self.server.world.itemGenerator.itemService
    
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
      connection.state = -1
      response = Message(MessageType.PasswordRequest)
    else:
      connection.state = 1
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
    chatText = "Player " + connection.player.name + " has connected!"
    log.debug(chatText)
    self.__sendPlayerDataMessageFor(connection)

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
    response = Message(MessageType.InventoryData)
    response.appendByte(connection.clientNumber)
    response.appendByte(slot)
    response.appendByte(amount)
    response.appendRaw(itemName)
    self.messageSender.sendMessageToOtherClients(response, connection)

  def __processRequestWorldDataMessage(self, message, connection):
    world = self.server.world
    if connection.state == 1:
      connection.state = 2
    self.messageSender.sendWorldDataMessageTo(connection, world)
  
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
            if tile.isImportant():
              tileSectionMsg.appendInt16(tile.frameX)
              tileSectionMsg.appendInt16(tile.frameY)
          if tile.wall > 0:
            tileSectionMsg.appendByte(tile.wall)
          if tile.liquid > 0:
            tileSectionMsg.appendByte(tile.liquid)
            tileSectionMsg.appendByte(tile.isLava)
        connection.socket.send(tileSectionMsg.create())  

  def __sendItemInfo(self, connection):
    for i in range(len(self.server.world.items)):
      item = self.server.world.items[i]
      if item.active:
        itemInfoMessage = self.__buildItemInfoMessage(i, item.position[0], item.position[1], item.velocity[0], item.velocity[1], item.stackSize, item.itemName)
        connection.socket.send(itemInfoMessage.create())
        itemOwnerInfoMsg = self.__buildItemOwnerInfoMessage(i, item.owner)
        connection.socket.send(itemOwnerInfoMsg.create())

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
    if connection.state == 2:
      connection.state = 3
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
    message = Message(MessageType.Message)
    message.appendByte(255) # who sent the message? 255 means server sent message
    message.appendByte(255) # R 
    message.appendByte(0) # G
    message.appendByte(0) # B
    message.appendRaw(self.server.motd)
    connection.socket.send(message.create())

  def __sendPlayerUpdateTwoMessageFor(self, connection):
    playerUpdateTwoMsg = Message(MessageType.PlayerUpdateTwo)
    playerUpdateTwoMsg.appendByte(connection.clientNumber)
    playerUpdateTwoMsg.appendByte(True)
    self.__sendMessageToOtherClients(playerUpdateTwoMsg, connection)

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

  def __processSpawnMessage(self, message, connection):
    clientNumber = struct.unpack('<B', message.buf[1])[0]
    spawnX, spawnY = struct.unpack('<ii', message.buf[2:10])
    connection.player.spawn = (spawnX, spawnY)
    connection.player.active = True
#    if connection.state >= 3:
      # we have to send spawn data to the other clients and NOT this one...
    response = Message(MessageType.Spawn)
    response.appendByte(clientNumber)
    response.appendInt(spawnX)
    response.appendInt(spawnY)
    self.__sendMessageToOtherClients(response, connection)
 #     if connection.state == 3:
  #      connection.state = 10
    self.messageSender.syncPlayers()
    self.__greetPlayer(connection)
    cons = self.connectionManager.getConnectionList()
    newCons = []
    for c in cons:
      if c.authed and c.clientNumber != connection.clientNumber:
        newCons.append(c)
    self.messageSender.sendChatMessageFromServer("%s has joined!" % (connection.player.name), (255, 255, 15), newCons)

  def __sendMessageToOtherClients(self, message, clientToIgnore):
    cons = self.connectionManager.getConnectionList()
    for c in cons:
      if c.authed and c.clientNumber != clientToIgnore.clientNumber:
        c.socket.send(message.create())

  def __processPlayerHealthUpdateMessage(self, message, connection):
    if not self.__checkClientIdFor(message, connection):
      return
    clientNumber = struct.unpack('<B', message.buf[1])[0]
    connection.player.statLife, connection.player.statLifeMax = struct.unpack('<hh', message.buf[2:6])
    if connection.player.statLife <= 0:
      connection.player.dead = True
    self.__sendPlayerHealthUpdateMessageFor(connection)

  def __processPlayerManaUpdateMessage(self, message, connection):
    if not self.__checkClientIdFor(message, connection):
      return
    clientNumber = message.buf[1]
    connection.player.mana, connection.player.manaMax = struct.unpack('<hh', message.buf[2:6])
    self.__sendPlayerManaUpdateMessageFor(connection)

  def __processSendSpawnMessage(self, message, connection):
    log.warning("need to implement got send spawn message")

  def __processPlayerUpdateOneMessage(self, message, connection):
    if not self.__checkClientIdFor(message, connection):
      return
    num = struct.unpack('<B', message.buf[1])[0]
    connection.player.playerFlags = struct.unpack('<B', message.buf[2])[0]
    connection.player.selectedItem = struct.unpack('<B', message.buf[3])[0]
    #connection.player.posX,connection.player.posY = struct.unpack('<ff', message.buf[4:12])
    newPlayerPosX, newPlayerPosY = struct.unpack('<ff', message.buf[4:12])
    connection.player.updatePosition((newPlayerPosX, newPlayerPosY))
    connection.player.velX,connection.player.velY = struct.unpack('<ff', message.buf[12:20])
    response = Message(MessageType.PlayerUpdateOne)
    response.appendByte(num)
    response.appendByte(connection.player.playerFlags)
    response.appendByte(connection.player.selectedItem)
    response.appendFloat(connection.player.posX)
    response.appendFloat(connection.player.posY)
    response.appendFloat(connection.player.velX)
    response.appendFloat(connection.player.velY)
    self.__sendMessageToOtherClients(response, connection)
    try:
      if connection.player.hasMoved():
        for i in range(len(self.server.world.items)):
          item = self.server.world.items[i]
          if item.active and item.collidesWithPlayer(connection.player):
            itemOwnerInfoMsg = self.__buildItemOwnerInfoMessage(i, connection.clientNumber)
            self.messageSender.sendMessageToAllClients(itemOwnerInfoMsg)
    except Exception as ex:
      log.error(ex)
      
  def __processZoneInfoMessage(self, message, connection):
    #log.debug("Got ZoneInfoMessage")
    #log.debug(str(len(message.buf[2:])))
    clientNumber = struct.unpack('<B', message.buf[1])[0]
#    zoneEvil,zoneMeteor,zoneDungeon,zoneJungle = struct.unpack('<????', message.buf[2:6])
    # not sure what we do with those ^ yet...

  def __processNpcTalkMessage(self, message, connection):
    #log.debug("Got NpcTalkMessage")
    pass
    
  def __processManipulateTileMessage(self, message, connection):
    tileType = struct.unpack('<B', message.buf[1])[0]
    x, y = struct.unpack('<ii', message.buf[2:10])
    newType = struct.unpack('<B', message.buf[10])[0]
    flag = (newType == 1)
    if not flag:
      if tileType == 0 or tileType == 2:
        pass # antispam stuff
      elif tileType == 1 or tileType == 3:
        pass # antispam stuff
    item = None
    itemNum = None
    if tileType == 0:
      (item, itemNum) = self.server.world.killTile((x,y), flag, False, False)
    elif tileType == 1:
      self.server.world.placeTile(x, y, newType, False, True, -1)
    elif tileType == 2:
      pass # kill wall
    elif tileType == 3:
      pass # place wall
    elif tileType == 4:
      (item, itemNum) = self.server.world.killTile((x,y), flag, False, True)
    response = Message(MessageType.ManipulateTile)
    response.appendByte(tileType)
    response.appendInt(x)
    response.appendInt(y)
    response.appendByte(newType)
    self.messageSender.sendMessageToOtherClients(response, connection)
    if tileType == 1 and newType == 53:
      self.__sendTileSquare(connection, x, y, 1)
    if item:
      itemInfoMessage = self.__buildItemInfoMessage(itemNum, item.position[0], item.position[1], item.velocity[0], item.velocity[1], item.stackSize, item.itemName)
      self.messageSender.sendMessageToAllClients(itemInfoMessage)

  def __processMessageMessage(self, message, connection):
    clientNumber = struct.unpack('<B', message.buf[1])[0]
    r,g,b = struct.unpack('<BBB', message.buf[2:5])
    text = message.buf[5:]
    if text.startswith("/item "):
      regex = r"/item ([A-Za-z']+)\s*([A-Za-z']*)\s*([A-Za-z']*)\s*([A-Za-z']*)\s*(\d*)"
      match = re.match(regex, text)
      itemName = match.group(1).encode('ascii', 'ignore')
      for i in range(2, 5):
        if match.group(i) != '':
          itemName = itemName + " " + match.group(i).encode('ascii', 'ignore')
      amount = 1
      if match.group(5) != '':
        amount = clamp(int(match.group(5)), 1, 255)
      item = self.itemService.getItemByName(itemName)
      if not item:
        self.messageSender.sendChatMessageFromServer("Unknown item: " + itemName, (255, 255, 15), [connection])
        return
      itemIndex = self.server.world.getNextItemNum()
      try:
        itemMsg = self.__buildItemInfoMessage(itemIndex, connection.player.posX + 5, connection.player.posY, 0.19, -1.8, amount, itemName)
      except Exception as ex:
        log.error(ex)
      item.setAmount(amount)
      item.active = True
      self.server.world.items[itemIndex] = item
      log.debug("Sending item: " + itemName + " to " + connection.player.name)
      self.messageSender.sendMessageToAllClients(itemMsg)
      itemOwnerMsg = self.__buildItemOwnerInfoMessage(itemIndex, connection.clientNumber)
      self.messageSender.sendMessageToAllClients(itemOwnerMsg)
    elif text.startswith("/loc"):
      chatText = "Your location (" + str(connection.player.posX) + ", " + str(connection.player.posY) + ")"
      self.messageSender.sendChatMessageFromServer(chatText, (255, 255, 15), [connection])
    else:
      response = Message(MessageType.Message)
      response.appendByte(clientNumber)
      response.appendByte(r)
      response.appendByte(g)
      response.appendByte(b)
      response.appendRaw(text)
      self.messageSender.sendMessageToAllClients(response) 

  def __buildItemOwnerInfoMessage(self, itemIndex, clientNumber):
    msg = Message(MessageType.ItemOwnerInfo)
    msg.appendInt16(itemIndex)
    msg.appendByte(clientNumber)
    return msg

  def __processItemInfoMessage(self, message, connection):
    itemNum = struct.unpack('<h', message.buf[1:3])[0]
    posX, posY,velX,velY = struct.unpack('<ffff', message.buf[3:19])
    stack2 = struct.unpack('<B', message.buf[19])[0]
    itemName = message.buf[20:]
    if itemName == "0":
      if itemNum < 200:
        self.server.world.items[itemNum].active = False
        message = self.__buildItemInfoMessage(itemNum, posX, posY, velX, velY, stack2, itemName)
        self.messageSender.sendMessageToAllClients(message)
    else:
      flag = (itemNum == 200)
      item = self.itemService.getItemByName(itemName)
      if flag:
        itemNum = self.server.world.getNextItemNum()
        self.server.world.items[itemNum] = item
      self.server.world.items[itemNum].setAmount(stack2)
      self.server.world.items[itemNum].position = (posX, posY)
      self.server.world.items[itemNum].velocity = (velX, velY)
      self.server.world.items[itemNum].active = True
      self.server.world.items[itemNum].owner = 255
      message = self.__buildItemInfoMessage(itemNum, posX, posY, velX, velY, stack2, itemName)
      if flag:        
        self.messageSender.sendMessageToAllClients(message)
      else:
        self.messageSender.sendMessageToOtherClients(message, connection)
        
  def __buildItemInfoMessage(self, itemNum, posX, posY, velX, velY, stack2, itemName):
    message = Message(MessageType.ItemInfo)
    message.appendInt16(itemNum)
    message.appendFloat(posX)
    message.appendFloat(posY)
    message.appendFloat(velX)
    message.appendFloat(velY)
    message.appendByte(stack2)
    message.appendRaw(itemName)
    return message

  def __processItemOwnerInfoMessage(self, message, connection):
    itemNumber = struct.unpack('<h', message.buf[1:3])[0]
    owner = struct.unpack('<B', message.buf[3])[0]
    #owner = 255
    self.server.world.items[itemNumber].owner = owner
    response = Message(MessageType.ItemOwnerInfo)
    response.appendInt16(itemNumber)
    response.appendByte(owner)
    self.messageSender.sendMessageToAllClients(response)
    
  def __processProjectileMessage(self, message, connection):
    projectileIdentity = struct.unpack('<h', message.buf[1:3])[0]
    posX, posY, velX, velY, knockback, damage, owner, projectileType = struct.unpack('<fffffhBB', message.buf[3:27])
    ai1, ai2 = struct.unpack('<ff', message.buf[27:35])
    response = Message(MessageType.Projectile)
    response.appendInt16(projectileIdentity)
    response.appendFloat(posX)
    response.appendFloat(posY)
    response.appendFloat(velX)
    response.appendFloat(velY)
    response.appendFloat(knockback)
    response.appendInt16(damage)
    response.appendByte(owner)
    response.appendByte(projectileType)
    response.appendFloat(ai1)
    response.appendFloat(ai2)
    self.messageSender.sendMessageToOtherClients(response, connection)
    
  def __processProjectileOwnerInfoMessage(self, message, connection):
    projectileIdentity = struct.unpack('<h', message.buf[1:3])[0]
    owner = struct.unpack('<B', message.buf[3])[0]
    response = Message(MessageType.ProjectileOwnerInfo)
    response.appendInt16(projectileIdentity)
    response.appendByte(owner)
    self.messageSender.sendMessageToOtherClients(response, connection)
    
  def __processTileSquareMessage(self, message, connection):
    num9, num10, num11 = struct.unpack('<hii', message[1:11])
    num = 11
    for j in range(num10, num10 + num9):
      for k in range(num11, num11 + num9):
        tileFlags = struct.unpack('<B', message[num])[0]
        num += 1
        active = self.server.world.tiles[j][k].isActive
        self.server.world.tiles[j][k] = self.server.world.tiles[j][k].copy()
        self.server.world.tiles[j][k].isActive = ((tileFlags and 1) == 1)
        self.server.world.tiles[j][k].isLighted = ((tileFlags and 2) == 2)
        if ((tileFlags and 4) == 4):
          self.server.world.tiles[j][k].wall = 1
        else:
          self.server.world.tiles[j][k].wall = 0
        if ((tileFlags and 8) == 8):
          self.server.world.tiles[j][k].liquid = 1
        else:
          self.server.world.tiles[j][k].liquid = 0
        if self.server.world.tiles[j][k].isActive:
          tileType = self.server.world.tiles[j][k].tileType
          self.server.world.tiles[j][k].tileType = struct.unpack('<B', message[num])[0]
          num += 1
          if self.server.world.tiles[j][k].isImportant():
            self.server.world.tiles[j][k].frameX = struct.unpack('<h', message[num:num+2])[0]
            num += 2
            self.server.world.tiles[j][k].frameY = struct.unpack('<h', message[num:num+2])[0]
            num += 2
          else:
            if not active or self.server.world.tiles[j][k].tileType != tileType:
              self.server.world.tiles[j][k].frameX = -1
              self.server.world.tiles[j][k].frameY = -1
        if self.server.world.tiles[j][k].wall > 0:
          self.server.world.tiles[j][k].wall = struct.unpack('<B', message[num])[0]
          num += 1
        if self.server.world.tiles[j][k].liquid > 0:
          self.server.world.tiles[j][k].liquid = struct.unpack('<B', message[num])[0]
          num += 1
          self.server.world.tiles[j][k].isLava = struct.unpack('<?', message[num])[0]
          num += 1
    self.server.world.rangeFrame(num10, num11, num10 + num9, num11 + num9)
    response = Message(MessageType.TileSquare)
    response.appendRaw(messsage[1:])
    self.messageSender.sendMessageToOtherClients(response, connection)
    #response.appendInt16(num9)
    #response.appentInt(num10)
    #response.appendInt(num11)
    
        
          
    

  def processMessage(self, message, connection):
    try:
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
      elif message.messageType == MessageType.Unknown15:
        self.messageSender.syncPlayers()
      elif message.messageType == MessageType.Message:
        self.__processMessageMessage(message, connection)
      elif message.messageType == MessageType.ItemInfo:
        self.__processItemInfoMessage(message, connection)
      elif message.messageType == MessageType.ItemOwnerInfo:
        self.__processItemOwnerInfoMessage(message, connection)
      elif message.messageType == MessageType.Projectile:
        self.__processProjectileMessage(message, connection)
      elif message.messageType == MessageType.ProjectileOwnerInfo:
        self.__processProjectileOwnerInfoMessage(message, connection)
      elif message.messageType == MessageType.TileSquare:
        self.__processTileSquareMessage(message, connection)
      else:
        log.warning("Need to implement message type: " + str(message.messageType))
    except Exception as ex:
      log.error(ex)
