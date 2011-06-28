import logging.config

from net.server import TerrariaServer
from game.worldmanager import WorldManager
from game.world import World
from game.tile import *
from util.tileutil import *
from game.item import Item

def debug_world():
  w = World()
  w.time = 13500.0
  w.name = "Debug"
  w.width = 800
  w.height = 600
  w.spawn = (100,198)
  w.isDay = True
  air = AirTile()
  dirt = DirtTile()
  stone = StoneTile()
  
  # tileType 4 and 5 causes stackoverflow on clients...
  # iron = tileType 6
  # copper = tileType 7
  # gold tileType 8
  # silver tileType 9
  # closeddoor tileType 10
  # opendoor tileType 11
  # some background tile tileType 12
  # empty jar background tileType 13
  # platform background tileType 14
  # platofrm background tileType 15
  # weird looking thing tileType 16
  # half a stone tile? tileType 17
  # weird platform background: tileType 18
  # full platform tile: tileType 19
  # weird plant background tileType 20
  # chest tileType 21
  # demonite tileType 22
  # corruption tileType 23
  # weird half corruption tileType 24 (crashes client when mined)
  # ebonstone tileType 25
  # weird background tileType 26
  # weird half background tileType 27
  # weird background tileType 28
  # piggy bank tileType 29
  # wood tileType 30
  # weird half background thing tileType 31
  # corruption stuff tileType 32
  # weird candle background thing tileType 33
  # blank? tileType 34
  # blank? crashes client tileType 35
  # blank? tileType 36
  # meteorite tileType 37
  # gray brick tileType 38
  # red brick tileType 39
  # clay tileType 40
  # blue brick tileType 41
  # weird background tile 42
  # sand: tileType 53  
  # 60 is mud with grass

  # tile notes:
  # dirt appears to always be:
  # isActive = True
  # tileType = 0
  # isLighted = True
  # frameX = -1
  # frameY = -1

  # wall 2 is dirt
  
  w.tiles = [[air for y in range(w.height)] for x in range(w.width)]
  for x in range(w.width):
    for y in range(200, 400):
      if x > 100:
        w.tiles[x][y] = Tile()
        w.tiles[x][y].tileType = 53 # sand
        w.tiles[x][y].isActive = True
        w.tiles[x][y].isLighted = True
        w.tiles[x][y].frameX = -1
        w.tiles[x][y].frameY = -1
      else:
        w.tiles[x][y] = dirt
  
  w.worldSurface = 300
  w.rockLayer = 400
  w.waterLine = (w.rockLayer + w.height) / 2
  w.waterLine = w.waterLine + -50
  w.lavaLine = w.waterLine + 60
  item = Item("Iron Pickaxe", 1)
  item.position = (557, 3180)
  item.active = True
  item.owner = 255
  #w.items[3] = item
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
