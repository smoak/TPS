from repository.itemrepository import ItemRepository

class ItemService(object):
  def __init__(self):
    self.itemRepository = ItemRepository()
    
  def getItemByType(self, type):
    pass