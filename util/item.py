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
      newItem = self.itemService.getItemByType(itemType)
      newItem.stackSize = amount
      newItemX = (newItemX + NEW_ITEM_WIDTH / 2 - newItem.width / 2)
      newItemY = (newItemY + NEW_ITEM_HEIGHT / 2 - newItem.height / 2)
      newItem.position = (newItemX, newItemY)
      newItemVelX = random.randint(-20, 21) * 0.1
      newItemVelY = random.randint(-30, -10) * 0.1
      newItem.velocity = (newItemVelX, newItemVelY)
      newItem.active = True
    
    return newItem