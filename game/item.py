import math, logging

MAX_STACK_SIZE = 250

log = logging.getLogger()

class Item:
  def __init__(self, itemName, stackSize):
    self.itemName = itemName
    self.setAmount(stackSize)
    self.position = (0,0)
    self.velocity = (0,0)
    self.owner = 255
    self.itemType = 0
    self.width = 0
    self.height = 0
    self.active = False
    
  def __colWidth(self):
    return self.width * 0.90
    
  def __colXOffset(self):
    return (self.width - self.__colWidth()) / 2
    
  def __colHeight(self):
    return self.height * 0.90
    
  def __colYOffset(self):
    return (self.height - self.__colHeight()) / 2
    
  def collidesWithPlayer(self, player):
    if not player.hasSpaceFor(self):
      return False
    # num3 = math.fabs(player.posX + (player.width / 2.0) - self.position[0] - (self.width / 2.0)) + math.fabs(player.posY + (player.height / 2.0) - self.position[1] - self.height)
    # log.debug("collidesWithPlayer (%s) num3=%d" % (player.name, num3))
    # return num3 < -1
    
    left1 = self.position[0] + self.__colXOffset()
    left2 = player.posX + ((player.width - (player.width * 0.90)) / 2)
    right1 = left1 + self.__colWidth()
    right2 = player.posX + (player.width * 0.90)
    top1 = self.position[1] + self.__colYOffset()
    top2 = player.posY + ((player.height - (player.height * 0.90)) / 2)
    bottom1 = top1 + self.__colHeight()
    bottom2 = top2 + (player.height * 0.90)
    
    if (bottom1 < top2) or (top1 > bottom2) or (right1 < left2) or (left1 > right2):
      return True
      
    return False

  def setAmount(self, stackSize):
    self.stackSize = min(stackSize, MAX_STACK_SIZE)
    
  def __repr__(self):
    return "<Item('%s', Type=%d, %dx%d)>" % (self.itemName, self.itemType, self.width, self.height)
