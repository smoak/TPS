from inventory import Inventory

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
    self.inventory = Inventory()
