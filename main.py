import logging.config

from net.server import TerrariaServer
from game.worldmanager import WorldManager
from game.world import World
from game.tile import *
from util.tileutil import *

def debug_world():
  w = World()
  w.name = "Debug"
  w.width = 800
  w.height = 600
  w.spawn = (30,199)
  air = Tile()
  air.isActive = False
  air.isLighted = False
  air.tileType = 0
  air.frameX = 0
  air.frameY = 0
  air.wall = 0
  air.isLava = False
  air.liquid = 0
  
  w.tiles = [[air for y in range(w.height)] for x in range(w.width)]
  for x in range(0, w.width):
    for y in range(200, w.height):
      w.tiles[x][y] = Tile()
      w.tiles[x][y].tileType = 0
      w.tiles[x][y].isActive = True
      w.tiles[x][y].isLighted = True
      w.tiles[x][y].frameX = -1
      w.tiles[x][y].frameY = -1
  
  w.worldSurface = 200
  w.rockLayer = 400
  w.waterLine = (w.rockLayer + w.height) / 2
  w.waterLine = w.waterLine + -50
  w.lavaLine = w.waterLine + 60
  
  return w

def main():
  
  logging.config.fileConfig('logging.conf')
 # worldManager = WorldManager()
#  world = worldManager.load('world2')
  world = debug_world()
  s = TerrariaServer("", 7777, world, None)
  s.start()

if __name__ == '__main__':
  main()
