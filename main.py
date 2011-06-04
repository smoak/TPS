import logging.config

from net.server import TerrariaServer
from game.worldmanager import WorldManager

def main():
  worldManager = WorldManager()
  
  logging.config.fileConfig('logging.conf')
  s = TerrariaServer("", 7777, None)
  s.start()

if __name__ == '__main__':
  main()
