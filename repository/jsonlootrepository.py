import json, os.path, sys

basepath = os.path.dirname(__file__)
JSON_FILE = "tiles.json"
filepath = os.path.abspath(os.path.join(basepath, "..", "..", JSON_FILE))

class JsonLootRepository(object):
  def __init__(self):
    self.tiles = json.load(open(JSON_FILE, 'rb'))
    
  def getTileLootTable(self, tileType):
    for t in self.tiles:
      if t['tileType'] == tileType:
        return t['drops']
    return []