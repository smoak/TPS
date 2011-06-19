import json, os.path, sys

basepath = os.path.dirname(__file__)
JSON_FILE = "items.json"
filepath = os.path.abspath(os.path.join(basepath, "..", "..", JSON_FILE))

class JsonItemRepository(object):
  def __init__(self):
    self.items = json.load(open(JSON_FILE, 'rb'))
    
  def getItemByType(self, type):
    for item in self.items:
      if item['type'] == type:
        return item
    return None
    
  def getItemByName(self, name):
    for item in self.items:
      if item['name'] == name:
        return item
    return None