import ConfigParser

from config.server import ServerConfig
from net.server import TerrariaServer

def load_config():
  config = ConfigParser.RawConfigParser()
  config.read('server.cfg')
  return ServerConfig().from_config(config)

def load_world(worldPath):
  return None

def main():
  config = load_config()
  world = load_world(config.worldPath)
  server = TerrariaServer(config, world)
  server.run()

if __name__ == '__main__':
  main()
