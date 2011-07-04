from net.message import MessageType
from message import BaseMessage

class TileSquareMessage(BaseMessage):
  """
  Represents a tile square message.
  """
  def __init__(self):
    BaseMessage.__init__(self)
    self._messageType = MessageType.TileSquare
    self.size = 0
    self.tileX = 0
    self.tileY = 0
    self.world = None
    
  def create(self):
    self.writeInt16(self.size)
    halfWidth = (self.size - 1) / 2
    self.writeInt32(self.tileX - halfWidth)
    self.writeInt32(self.tileY - halfWidth)
    for j in range((self.tileX - halfWidth), (self.tileX - halfWidth) + self.size):
      for k in range((self.tileY - halfWidth), (self.tileY - halfWidth) + self.size):
        tileFlags = self.world.tiles[j][k].getFlags()
        self.writeByte(tileFlags)
        if self.world.tiles[j][k].isActive:
          self.writeByte(self.tiles[j][k].tileType)
          if self.world.tiles[j][k].isImportant():
            self.appendInt16(self.world.tiles[j][k].frameX)
            self.appendInt16(self.world.tiles[j][k].frameY)
        if self.world.tiles[j][k].wall > 0:
          self.appendByte(self.world.tiles[j][k].wall)
        if self.world.tiles[j][k].liquid > 0:
          self.appendByte(self.world.tiles[j][k].liquid)
          self.appendByte(self.world.tiles[j][k].isLava)
    return BaseMessage.create(self)

    
class ManipulateTileMessage(BaseMessage):
  """
  Manipulate tile message. Sent when a tile changes
  due to mining or some other reason.
  """
  
  class ActionType:
    """
    Enum for types of manipulating tiles
    """
    KillTile = 0x00
    PlaceTile = 0x01  
    KillWall = 0x02
    PlaceWall = 0x03
    KillTileNoItem = 0x04
  
  def __init__(self):
    BaseMessage.__init__(self)
    self._messageType = MessageType.ManipulateTile
    self.tileX = -1
    self.tileY = -1
    self.action = ActionType.KillTile 
    # NOTE: When the ActionType = Kill{Tile,Wall}, this tileType acts as 
    # a bool indicating wheter the kill failed or succeeded. For all other
    # action types this tileType indicates the tileType to change to.    
    self.tileTypeToChangeTo = -1
    self.style = -1
    
  def create(self):
    self.writeByte(self.action)
    self.writeInt32(self.tileX)
    self.writeInt32(self.tileY)
    self.writeByte(self.tileTypeToChangeTo)
    return BaseMessage.create(self)