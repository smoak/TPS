import logging

from net.message import *
from net.messagebuilder import MessageBuilder

log = logging.getLogger()

class MessageSender(object):

  def __init__(self, connectionManager):
    self.connectionManager = connectionManager
    self.messageBuilder = MessageBuilder()

  def sendWorldUpdateToAllClients(self, world):
    worldUpdate = self.messageBuilder.buildWorldDataMessage(world)
    self.sendMessageToAllClients(worldUpdate)

  def sendWorldDataMessageTo(self, connection, world):
    msg = self.messageBuilder.buildWorldDataMessage(world)
    connection.socket.send(msg.create())

  def sendMessageToAllClients(self, message):
    cons = self.connectionManager.getConnectionList()
    for c in cons:
      if c.authed:
        c.socket.send(message.create())

  def sendPlayerDisconnectedToOtherClients(self, connection):
    self.__sendPlayerUpdateTwoMessageFor(connection)
    cons = self.connectionManager.getConnectionList()
    self.sendChatMessageFromServer(connection.player.name + " has disconnected!", (255, 255, 255), cons)

  def sendChatMessageFromServer(self, text, color, clients):
    message = Message(MessageType.Message)
    message.appendByte(255) # server sent message
    message.appendByte(color[0]) # Red
    message.appendByte(color[1]) # Green
    message.appendByte(color[2]) # Blue
    message.appendRaw(text)
    for ci in clients:
      if ci.authed:
        ci.socket.send(message.create())

  def syncPlayers(self):
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

  def __sendPlayerUpdateTwoMessageFor(self, connection):
    playerUpdateTwoMsg = Message(MessageType.PlayerUpdateTwo)
    playerUpdateTwoMsg.appendByte(connection.clientNumber)
    playerUpdateTwoMsg.appendByte(connection.player.active)
    self.sendMessageToOtherClients(playerUpdateTwoMsg, connection)

  def __sendPlayerUpdateOneMessageFor(self, connection):
    playerUpdateOneMessage = Message(MessageType.PlayerUpdateOne)
    playerUpdateOneMessage.appendByte(connection.clientNumber)
    playerUpdateOneMessage.appendByte(connection.player.playerFlags)
    playerUpdateOneMessage.appendByte(connection.player.selectedItem)
    playerUpdateOneMessage.appendFloat(connection.player.posX)
    playerUpdateOneMessage.appendFloat(connection.player.posY)
    playerUpdateOneMessage.appendFloat(connection.player.velX)
    playerUpdateOneMessage.appendFloat(connection.player.velY)
    self.sendMessageToOtherClients(playerUpdateOneMessage, connection)

  def __sendPlayerHealthUpdateMessageFor(self, connection):
    playerHealthUpdateMessage = Message(MessageType.PlayerHealthUpdate)
    playerHealthUpdateMessage.appendByte(connection.clientNumber)
    playerHealthUpdateMessage.appendInt16(connection.player.statLife)
    playerHealthUpdateMessage.appendInt16(connection.player.statLifeMax)
    self.sendMessageToOtherClients(playerHealthUpdateMessage, connection)
	
  def __sendPvpModeMessageFor(self, connection):
    pvpModeMessage = Message(MessageType.PvpMode)
    pvpModeMessage.appendByte(connection.clientNumber)
    pvpModeMessage.appendByte(False)
    self.sendMessageToOtherClients(pvpModeMessage, connection)

  def __sendPvpTeamMessageFor(self, connection):
    pvpTeamMessage = Message(MessageType.PvpTeam)
    pvpTeamMessage.appendByte(connection.clientNumber)
    pvpTeamMessage.appendByte(0) # TODO: implement pvp mode
    self.sendMessageToOtherClients(pvpTeamMessage, connection)
	
  def __sendPlayerManaUpdateMessageFor(self, connection):
    manaUpdateMessage = Message(MessageType.PlayerManaUpdate)
    manaUpdateMessage.appendByte(connection.clientNumber)
    manaUpdateMessage.appendInt(connection.player.mana)
    manaUpdateMessage.appendInt(connection.player.manaMax)
    self.sendMessageToOtherClients(manaUpdateMessage, connection)
	
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
    self.sendMessageToOtherClients(playerData, connection)

  def __sendInventoryFor(self, connection):
    # send inventory items
    i = 0
    for item in connection.player.inventory.items:   
      itemMessage = Message(MessageType.InventoryData)
      itemMessage.appendByte(connection.clientNumber)
      itemMessage.appendByte(i)
      itemMessage.appendByte(item.stackSize)
      itemMessage.appendRaw(item.itemName)
      self.sendMessageToOtherClients(itemMessage, connection)
      i += 1
      
    # send armor
    for armor in connection.player.armor.items:
      itemMessage = Message(MessageType.InventoryData)
      itemMessage.appendByte(connection.clientNumber)
      itemMessage.appendByte(i)
      itemMessage.appendByte(armor.stackSize)
      itemMessage.appendRaw(armor.itemName)
      self.sendMessageToOtherClients(itemMessage, connection)
      i += 1

  def sendMessageToOtherClients(self, message, clientToIgnore):
    cons = self.connectionManager.getConnectionList()
    for c in cons:
      if c.authed and c.clientNumber != clientToIgnore.clientNumber:
        c.socket.send(message.create())
