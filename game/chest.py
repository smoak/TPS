MAX_CHEST_ITEMS = 20

class Chest:
  def __init__(self):
    self.items = []
    self.x = 0
    self.y = 0

  def hasItems(self):
    for i in self.items:
      if i.itemType > 0 and i.stackSize > 0:
        return True
    return False