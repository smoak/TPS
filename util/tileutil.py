import logging

log = logging.getLogger()

def dumpTile(pos, tile):
  log.debug("======Tile Data=====")
  log.debug("Pos: " + str(pos[0]) + ", " + str(pos[1]))
  log.debug("Type: " + str(tile.tileType))
  log.debug("Active: " + str(tile.isActive))
  log.debug("FrameX: " + str(tile.frameX))
  log.debug("FrameY: " + str(tile.frameY))
  log.debug("Wall: " + str(tile.wall))
  log.debug("Lava: " + str(tile.isLava))
  log.debug("Lighted: " + str(tile.isLighted))
  log.debug("Liquid: " + str(tile.liquid))
  log.debug("Flags: " + str(tile.getFlags()))
  log.debug("=====    End =======")
