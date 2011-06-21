from repository.jsonlootrepository import JsonLootRepository
from game.loot import *

class LootService(object):
  def __init__(self):
    self.lootRepository = JsonLootRepository()
    
  def getTileLootTableFor(self, tile):
    return LootTable(self.lootRepository.getTileLootTable(tile.tileType))