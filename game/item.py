MAX_STACK_SIZE = 250

class Item:
  def __init__(self, itemName, stackSize):
    self.itemName = itemName
    self.stackSize = self.setAmount(stackSize)
    self.position = (0,0)
    self.velocity = (0,0)

  def setAmount(self, stackSize):
    self.stackSize = min(stackSize, MAX_STACK_SIZE)
