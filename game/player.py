class Player(object):
  """
  Represents a player in Terraria
  """
  
  def __init__(self):
    self.name = ""
    self.hair = None
    self.hairColor = None
    self.eyeColor = None
    self.shoeColor = None
    self.life = 0
    self.lifeMax = 0
    self.isMale = False
    self.skinColor = None
    self.shirtColor = None
    self.underShirtColor = None
    self.pantsColor = None
    self.difficulty = 0
    self.mana = 0
    self.manaMax = 0
    self.spawn = (-1,-1)
