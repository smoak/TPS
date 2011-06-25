import random, logging

from game.item import Item
from service.itemservice import ItemService
from service.loot import LootService

NEW_ITEM_WIDTH = 16
NEW_ITEM_HEIGHT = NEW_ITEM_WIDTH
log = logging.getLogger()

class ItemGenerator:
  def __init__(self):
    self.itemService = ItemService()
    self.lootService = LootService()
    
  def generateNewItem(self, x, y, width, height, itemType, stack):
    item = self.itemService.getItemByType(itemType)
    item.setAmount(stack)
    itemX = (x + width / 2 - item.width / 2)
    itemY = (y + height / 2 - item.height / 2)
    item.position = (itemX, itemY)
    newItemVelX = random.randint(-20, 21) * 0.1
    newItemVelY = random.randint(-30, -10) * 0.1
    item.velocity = (newItemVelX, newItemVelY)
    item.active = True
    return item
	
  def generateItemFromKillingTile(self, tile, tileX, tileY):
    newItemX =  tileX * 16
    newItemY =  tileY * 16
    newItem = None
    itemType = None
    amount = None
    try:
      itemType, amount = self.lootService.getTileLootTableFor(tile).chooseDrop()
    except Exception as ex:
      log.error(ex)
    if itemType and amount:
      newItem = self.generateNewItem(newItemX, newItemY, NEW_ITEM_WIDTH, NEW_ITEM_HEIGHT, itemType, amount)
    return newItem