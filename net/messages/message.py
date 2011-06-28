import struct

class BaseMessage(object):
  headerFormat = "<i"
  headerFormatLen = struct.calcsize(headerFormat)
  int16Format = "<h"
  int16FormatLen = struct.calcsize(int16Format)
  int32Format = "<i"
  int32FormatLen = struct.calcsize(int32Format)
  floatFormat = "<f"
  floatFormatLen = struct.calcsize(floatFormat)
  byteFormat = "<B"
  byteFormatLen = struct.calcsize(byteFormat)
  
  def __init__(self):
    self._messageLen = 0
    self._messageBuf = bytearray()
    self._messageType = -1
    self._currentPos = 0
    
  def create(self):
    return struct.pack(self.headerFormat, self._messageLen) + str(self._messageBuf)
    
  def deserialize(self, data):
    self._messageLen, = struct.unpack(self.headerFormat, data[self._currentPos:self._currentPos + self.headerFormatLen])
    self._currentPos += self.headerFormatLen
  
  def writeInt16(self, value):
    self._messageBuf.extend(struct.pack(self.int16Format, value))
    self._messageLen += self.int16FormatLen
    
  def writeInt32(self, value):
    self._messageBuf.extend(struct.pack(self.int32Format, value))
    self._messageLen += self.int32FormatLen
    
  def writeFloat(self, value):
    self._messageBuf.extend(struct.pack(self.floatFormat, value))
    self._messageLen += self.floatFormatLen
    
  def writeByte(self, value):
    self._messageBuf.extend(struct.pack(self.byteFormat, value))
    self._messageLen += self.byteFormatLen