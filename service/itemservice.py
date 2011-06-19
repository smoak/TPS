from repository.jsonitemrepository import JsonItemRepository
from game.item import Item

class ItemService(object):
  def __init__(self):
    self.itemRepository = JsonItemRepository()
    
  def getItemByType(self, type):
    entity = self.itemRepository.getItemByType(type)
    result = None
    if entity:
      result = Item(entity['name'], 1)
      self.__mapEntityToDomain(entity, result)
    return result
    
  def getItemByName(self, name):
    entity = self.itemRepository.getItemByName(name)
    result = None
    if entity:
      result = Item(entity['name'], 1)
      self.__mapEntityToDomain(entity, result)
    return result
    
  def __mapEntityToDomain(self, entity, domain):
    domain.width = entity['width']
    domain.height = entity['height']
    domain.itemType = entity['type']