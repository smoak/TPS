class SimpleDatabaseConfig(object):
  """
  Simple object for storing database configuration values
  """
  
  def __init__(self, databaseType, databaseName, userName, password, hostname, port):
    self.databaseType = databaseType
    self.databaseName = databaseName
    self.userName = userName
    self.password = password
    self.hostname = hostname
    self.port = port