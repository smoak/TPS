import ConfigParser

from config.server import ServerConfig
from net.server import TerrariaServer

def load_config():
  config = ConfigParser.RawConfigParser()
  config.read('server.cfg')
  return ServerConfig().from_config(config)

def main():
  config = load_config()
  server = TerrariaServer(config)
  server.run()

if __name__ == '__main__':
  main()
