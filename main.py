import logging.config

from net.server import TerrariaServer
from game.worldmanager import WorldManager

def main():
  
  logging.config.fileConfig('logging.conf')
  worldManager = WorldManager()
  world = worldManager.load('world2')
  s = TerrariaServer("", 7777, world, None)
  s.start()

if __name__ == '__main__':
  main()
