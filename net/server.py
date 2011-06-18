from twisted.internet import reactor

from net.protocol import TerrariaFactory
    
class TerrariaServer:
  def __init__(self, listenAddress, listenPort, world, password=None):
    self.listenAddress = listenAddress
    self.listenPort = listenPort
    self.world = world
    self.password = password
    
  def on_client_connect_success(self):
    print "Got connection!"
    
  def on_client_connect_fail(self, reason):
    print 'Connection failed: %s' % reason.getErrorMessage()
    
  def on_client_receive(self, msg):
    print "Got new message!"
    print type(msg[0])
    
  def start(self):
    print "Starting server..."
    self.server = TerrariaFactory(self.on_client_connect_success, self.on_client_connect_fail, self.on_client_receive)
    self.reactor = reactor.listenTCP(self.listenPort, self.server)
    print "Listening..."
    reactor.run()