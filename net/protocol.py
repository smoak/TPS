import struct

from twisted.internet import protocol
from twisted.protocols.basic import IntNStringReceiver

class TerrariaProtocol(IntNStringReceiver):
  structFormat = "<L"
  prefixLength = struct.calcsize(structFormat)
  
  def stringReceived(self, string):
    self.factory.got_msg(string)
    
  def connectionMade(self):
    self.factory.clientReady(self)
    
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
    
  def send_msg(self, msg):
    if self.client:
      self.client.sendString(msg)
  