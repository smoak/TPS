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
  TileSection = 0x0A # 10
  TileConfirmed = 0x0B # 11
  Spawn = 0x0C # 12
  PlayerUpdateOne = 0x0D # 13
  PlayerUpdateTwo = 0x0E # 14
  Unknown15 = 0x0F # 15
  PlayerHealthUpdate = 0x10 # 16
  ManipulateTile = 0x11 # 17
  ItemInfo = 0x15 # 21
  ItemOwnerInfo = 0x16 # 22
  NpcInfo = 0x17 # 23
  Unknown24 = 0x18 # 24
  Message = 0x19 # 25
  Projectile = 0x1B # 27
  Unknown28 = 0x1C # 28
  PvpMode = 0x1E # 30
  ZoneInfo = 0x24 # 36
  PasswordRequest = 0x25 # 37
  PasswordResponse = 0x26 # 38
  NpcTalk = 0x28 # 40
  PlayerManaUpdate = 0x2A # 42
  PvpTeam = 0x2D # 45
  SendSpawn = 0x31 # 49

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

  def appendFloat(self, f):
    self.buf = self.buf + struct.pack('<f', f)
    self.size = len(self.buf)

  def create(self):
    result = struct.pack('<i', self.size)
    result = result + self.buf
    return result
    
