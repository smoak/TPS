import socket
import thread
import logging

from connectioninfo import ConnectionInfo

log = logging.getLogger("TerrariaServer")

class NetworkState:
  Starting = 0
  Running = 1
  Closing = 2
  Closed = 3
  Error = 4

class ConnectionManager:

  def __init__(self):
    self.__connections = []
    self.locker = thread.allocate_lock()

  def connectionCount(self):
    connectionCount = 0
    self.locker.acquire()
    connectionCount = len(self.__connections)
    self.locker.release()
    return connectionCount

  def addConnection(self, connection):
    self.locker.acquire()
    self.__connections.append(connection)
    self.locker.release()

  def removeConnection(self, connection):
    connection.socket.shutdown(socket.SHUT_RDWR)
    connection.socket.close()
    self.locker.acquire()
    self.__connections.remove(connection)
    self.locker.release()

class TerrariaServer:

  def __init__(self, listenAddr, listenPort, password=None):
    self.listenAddress = listenAddr
    self.listenPort = listenPort
    self.password = password
    self.networkState = NetworkState.Closed
    self.connectionManager = ConnectionManager()

  def __setupSocket(self):
    try:
      self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.socket.bind((self.listenAddress, self.listenPort))
      self.socket.listen(5)
      self.networkState = NetworkState.Running
    except Exception as ex:
      print ex
      self.networkState = NetworkState.Error

  def __mainLoop(self):
    while self.networkState == NetworkState.Running:
      (clientsock, clientaddr) = self.socket.accept()
      # New connection here
      #log.debug("New connection")
      print "New connection"
      connection = ConnectionInfo(clientsock, clientaddr, self.connectionManager.connectionCount() + 1)
      self.connectionManager.addConnection(connection)

  def start(self):
    self.__setupSocket()
    self.__mainLoop()
     
