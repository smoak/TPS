import logging
import logging.config

GLOBAL_SECTION = "Global"
WORLD_SECTION = "World"


class ServerConfig:
  def __init__(self):
    self.listenAddress = None
    self.listenPort = None
    self.serverPassword = None
    self.worldPath = None

  def from_config(self, config):
    self.listenAddress = config.get(GLOBAL_SECTION, "listen_ip")
    self.listenPort = int(config.get(GLOBAL_SECTION, "port"))
    self.serverPassword = config.get(GLOBAL_SECTION, "password")
    self.worldPath = config.get(WORLD_SECTION, "world_path")
    if config.get(GLOBAL_SECTION, "log_enabled"):
      logging.config.fileConfig('logging.cfg')
    return self
