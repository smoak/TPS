class ConnectionInfo:

  def __init__(self, socket, address, clientNumber):
    self.socket = socket
    self.address = address
    self.clientNumber = clientNumber
    self.data = ""
