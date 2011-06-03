from item import Item

MAX_INVENTORY_SLOTS = 52

class Inventory:
  def __init__(self):
    self.items = []
    for i in range(MAX_INVENTORY_SLOTS):
      self.items.append(Item("Empty", 1))

  def setSlot(self, slot, itemName, stackSize):
    if slot < 0 or slot > MAX_INVENTORY_SLOTS:
      return
    self.items[slot] = Item(itemName, stackSize)

  def remove(self, item):
    a = item.stackSize
    while a > 0:
      for i in self.items:
        if i.itemName == item.itemName:
          while i.stackSize > 0 and a > 0:
            item.setAmount(i.stackSize - 1)
            a -= 1
