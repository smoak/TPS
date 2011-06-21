import random

class LootTable(object):
  def __init__(self, drops):
    self.drops = drops
    
  def __rollForDrop(self, drop):
    return random.randint(1, 100) <= drop['chance']
  
  def chooseDrop(self):
    result = (None, None)
    if self.drops:
      for d in self.drops:
        if self.__rollForDrop(d):
          result = (d['itemType'], d['amount'])
          break
    return result