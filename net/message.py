import struct

class MessageType:
  ConnectionRequest = 0x01
  Disconnect = 0x02
  RequestPlayerData = 0x03
  PlayerData = 0x04
  InventoryData = 0x05
  RequestWorldData = 0x06
  WorldData = 0x07
  TileBlockRequest = 0x08
  TileLoading = 0x09
  TileSection = 0x0A
  TileConfirmed = 0x0B
  Spawn = 0x0C
  PlayerUpdateOne = 0x0D
  PlayerUpdateTwo = 0x0E
  PlayerHealthUpdate = 0x0F
  ManipulateTile = 0x10
  ItemInfo = 0x15
  ItemOwnerInfo = 0x16
  NpcInfo = 0x17
  Message = 0x19
  Projectile = 0x1B
  PvpMode = 0x1E
  ZoneInfo = 0x24
  PasswordRequest = 0x25
  PasswordResponse = 0x26
  NpcTalk = 0x28
  PlayerManaUpdate = 0x2A
  PvpTeam = 0x2D
  SendSpawn = 0x31

class Message:
  def __init__(self, messageType):
    self.messageType = messageType
    self.buf = struct.pack('<B', messageType)
    self.size = len(self.buf)

  def appendInt(self, i):
    self.buf = self.buf + struct.pack('<i', i)
    self.size = len(self.buf)    

  def appendInt16(self, i):
    self.buf = self.buf + struct.pack('<h', i)
    self.size = len(self.buf)

  def appendRaw(self, rawData):
    self.buf = self.buf + rawData
    self.size = len(self.buf)

  def appendByte(self, b):
    self.buf = self.buf + struct.pack('<B', b)
    self.size = len(self.buf)

  def create(self):
    result = struct.pack('<i', self.size)
    result = result + self.buf
    return result
    
