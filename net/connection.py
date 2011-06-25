import thread
import socket

class ConnectionManager:
  """
  Responsible for keeping track of each client connection
  """

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
    self.locker.acquire()
    self.__connections.remove(connection)
    connection.socket.shutdown(socket.SHUT_RDWR)
    connection.socket.close()
    self.locker.release()
    connection.player.active = False

  def getListOfSocketsForSelect(self):
    result = []
    self.locker.acquire()
    for ci in self.__connections:
      result.append(ci.socket)
    self.locker.release()
    return result

  def getConnectionList(self):
    result = []
    self.locker.acquire()
    result = self.__connections
    self.locker.release()
    return result

  def findConnection(self, socket):
    result = None
    self.locker.acquire()
    for ci in self.__connections:
      if ci.socket == socket:
        result = ci
        break
    self.locker.release()
    return result

  def getNewClientId(self):
    clientId = 0
    idList = []
    self.locker.acquire()
    # get a list of the clientIds
    for ci in self.__connections:
      idList.append(ci.clientNumber)      
    self.locker.release()
    # now we just want to find the next available id
    while clientId in idList:
      clientId += 1
    return clientId
