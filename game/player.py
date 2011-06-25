from inventory import Inventory
from util.math import *
from common.events import EventHook

MAX_ARMOR_SLOTS = 11

class Player:

  def __init__(self):
    self.name = ""
    self.hairStyle = 0
    self.hairColor = (0,0,0)
    self.skinColor = (0,0,0)
    self.eyeColor = (0,0,0)
    self.shirtColor = (0,0,0)
    self.underShirtColor = (0,0,0)
    self.pantsColor = (0,0,0)
    self.shoeColor = (0,0,0) 
    self.inventory = Inventory(self)
    self.statLife = 0
    self.statLifeMax = 0
    self.mana = 0
    self.manaMax = 0
    self.posX = 0
    self.posY = 0
    self.velX = 0
    self.velY = 0
    self.selectedItem = 0
    self.dead = False
    self.playerFlags = 0
    self.armor = Inventory(self, MAX_ARMOR_SLOTS)
    self.active = False
    self.width = 20
    self.height = 42
    self.oldPosX = self.posX
    self.oldPosY = self.posY
    self.hardCore = False
    self.immune = False
    self.immuneTime = 0
    self.onKilled = EventHook()
    
  def hurt(self, damage, hitDirection, pvp = False, quiet = False, deathText = " was slain..."):
    if not self.immune:
      num = damage
      if pvp:
        num = num * 2
      num2 = calculateDamage(num, self.statDefense)
      if num2 >= 1.0:
        self.statLife -= num2
        self.immune = True
        self.immuneTime = 40
        if pvp:
          self.immuneTime = 8
        if self.statLife <= 0:
          self.statLife = 0
          self.killMe(num2, hitDirection, pvp, deathText)
        
  def killMe(self, damage, hitDirection, pvp = False, deathText = " was slain..."):
    pass
    # TODO: implement me
    
  def updatePosition(self, newPosition):
    self.oldPosX = self.posX
    self.oldPosY = self.posY
    self.posX = newPosition[0]
    self.posY = newPosition[1]
    
  def hasMoved(self):
    return self.oldPosX != self.posX or self.oldPosY != self.posY
    
  def hasSpaceFor(self, item):
    # Heart and Star always return True
    if item.itemType in [58,184]:
      return True
    num = 40
    # copper, silver, gold, platinum coins respectively
    if item.itemType in [71, 72, 73, 74]:
      num = 44
    # Check if we have any free inventory slots
    for i in range(num):
      if self.inventory.items[i].itemType == 0:
        return True
    # No free inventory slots so check to see if the item is already
    # in the players inventory and its not > maxStackSize
    for i in range(num):
      if self.inventory.items[i].itemType > 0 and self.inventory.items[i].stackSize < 250:
        if self.inventory.items[i].itemName == item.itemName:
          return True
    return False