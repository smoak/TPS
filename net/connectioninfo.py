class ConnectionInfo(object):

  __slots__ = ["socket", "address", "clientNumber", "data", "authed", "player", "state"]

  def __init__(self, socket, address, clientNumber):
    self.socket = socket
    self.address = address
    self.clientNumber = clientNumber
    self.data = ""
    self.authed = False
    self.player = None
    self.state = 0
