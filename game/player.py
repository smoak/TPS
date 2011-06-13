from inventory import Inventory

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