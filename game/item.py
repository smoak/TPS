MAX_STACK_SIZE = 250

class Item:
  def __init__(self, itemName, stackSize):
    self.itemName = itemName
    self.stackSize = self.setAmount(stackSize)

  def setAmount(self, stackSize):
    self.stackSize = min(stackSize, MAX_STACK_SIZE)
