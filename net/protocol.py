import struct

from twisted.internet import protocol

from net.session import Session

class TerrariaProtocol(protocol.Protocol, Session):
  headerFormat = "<I"
  headerFormatLen = struct.calcsize(headerFormat)
  MAX_LENGTH = 9999
    
  """
  This is called when the connection is first 
  established. 
  """        
  def connectionMade(self):
    self._messageBuffer = bytearray()
    self.sessionConnect(self.getClientAddress())

  """
  Returns the client's address and port in a tuple. For example
  ('127.0.0.1', 41917)
  """
  def getClientAddress(self):
    return self.transport.client

  """
  Called whenever data is received.
  """
  def dataReceived(self, data):
    self._messageBuffer.extend(data)
    while len(self._messageBuffer) >= self.headerFormatLen:
      length ,= struct.unpack(self.headerFormat, str(self._messageBuffer[:self.headerFormatLen]))
      if length > self.MAX_LENGTH:
        self.lengthLimitExceeded(length)
        break
      if len(self._messageBuffer) < length + self.headerFormatLen:
        break
      message = self._messageBuffer[self.headerFormatLen:length + self.headerFormatLen]
      self._messageBuffer = self._messageBuffer[length + self.headerFormatLen:]
      self.messageReceived(message)

  """
  Callback invoked when a length prefix greater than C{MAX_LENGTH} is
  received.  The default implementation disconnects the transport.

  @param length: The length prefix which was received.
  @type length: C{int}
  """
  def lengthLimitExceeded(self, length):
    self.transport.loseConnection()

  """
  Called when a full message is received
  from the client. The messageLen header
  is stripped out.
  """
  def messageReceived(self, message):
    pass

  """
  Sends a message to the client. 
  """
  def sendMessage(self, message):
    pass

    
class TerrariaFactory(protocol.ServerFactory):
  protocol = TerrariaProtocol
  
  def __init__(self, connect_success_callback, connect_fail_callback, recv_callback):
    self.connect_success_callback = connect_success_callback
    self.connect_fail_callback = connect_fail_callback
    self.recv_callback = recv_callback
    self.client = None
  
  def clientConnectionFailed(self, connector, reason):
    self.connect_fail_callback(reason)
    
  def clientReady(self, client):
    self.client = client
    self.connect_success_callback()
    
  def got_msg(self, msg):
    self.recv_callback(msg)
