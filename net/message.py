import struct

class Message:
  def __init__(self, messageType):
    self.messageType = messageType
    self.buf = struct.pack('<B', messageType)
    self.size = len(self.buf)

  def appendInt(self, i):
    self.buf = self.buf + struct.pack('<i', i)
    self.size = len(self.buf)    

  def appendRaw(self, rawData):
    print "appendRaw"
    self.buf = self.buf + rawData
    self.size = len(self.buf)

  def create(self):
    result = struct.pack('<i', self.size)
    result = result + self.buf
    return result
    
