import json, os.path, sys

basepath = os.path.dirname(__file__)
JSON_FILE = "projectiles.json"
filepath = os.path.abspath(os.path.join(basepath, "..", JSON_FILE))

class JsonProjectileRepository(object):
  def __init__(self):
    self.projectiles = json.load(open(filepath, 'rb'))
    
  def getProjectileByType(self, type):
    for projectile in self.projectiles:
      if projectile['type'] == type:
        return projectile
    return None
    
  def getItemByName(self, name):
    for projectile in self.projectiles:
      if projectile['name'] == name:
        return projectile
    return None