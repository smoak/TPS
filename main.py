import logging.config

from net.server import TerrariaServer
from game.worldmanager import WorldManager
from game.world import World
from game.tile import *
from util.tileutil import *

def debug_world():
  w = World()
  w.time = 13500.0
  w.name = "Debug"
  w.width = 800
  w.height = 600
  w.spawn = (100,199)
  air = AirTile()
  dirt = DirtTile()
  stone = StoneTile()
  
  w.tiles = [[air for y in range(w.height)] for x in range(w.width)]
  for x in range(80, w.width):
    for y in range(200, w.height):
      if x > 100:
        w.tiles[x][y] = Tile()
        w.tiles[x][y].tileType = 7
        w.tiles[x][y].isActive = True
        w.tiles[x][y].isLighted = True
        w.tiles[x][y].frameX = -1
        w.tiles[x][y].frameY = -1
      else:
        w.tiles[x][y] = stone
#      w.tiles[x][y] = dirt
       
  
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
