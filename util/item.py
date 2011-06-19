from game.item import Item

class ItemGenerator:
  def __init__(self, world):
    self.world = world
	
  def generateItemFromKillingTile(x, y):
    tile = self.world.tiles[x][y]
	  item = None
	  num3 = 0
    if tile.tileTye in [0, 2]:
      num3 = 2
    elif tile.tileType == 1:
      num3 = 3
    elif tile.tileType == 4:
      num3 = 8
    elif tile.tileType == 5:
      if tile.frameX >= 22 and tile.frameY >= 198:
        num3 = 27
      else:
        num3 = 9
    if num3 > 0:
      pass # create new item with type = num3 Item.NewItem(x * 16, y * 16, 16, 16, num3, 1, false);
      #item = Item("0", 1)
      #itemX = (16 * x) + 16 / 2 - 
	
	  return item