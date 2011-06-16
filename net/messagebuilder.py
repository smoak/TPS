from net.message import *

class MessageBuilder(object):

  def buildNpcInfoMessageFor(self, npc):
    message = Message(MessageType.NpcInfo)
    message.appendInt16(0)
    message.appendFloat(npc.posX)
    message.appendFloat(npc.posY)
    message.appendFloat(npc.velX)
    message.appendFloat(npc.velY)
    message.appendInt16(npc.target)
    message.appendByte(npc.directionX + 1)
    message.appendByte(npc.directionY + 1)
    message.appendInt16(npc.life)
    for ai in npc.ai:
      message.appendFloat(ai)
    message.appendRaw(npc.name)
    return message

  def buildWorldDataMessage(self, world):
    message = Message(MessageType.WorldData)
    message.appendInt(world.time)
    message.appendByte(world.isDay)
    message.appendByte(world.moonphase)
    message.appendByte(world.isBloodMoon)
    message.appendInt(world.width) # maxTilesX
    message.appendInt(world.height) # maxTilesY
    spawn = world.spawn
    message.appendInt(spawn[0])
    message.appendInt(spawn[1])
  
    message.appendInt(world.worldSurface)
    message.appendInt(world.rockLayer)
     # NOTE: This is 0 because Terraria saves the world id
    # incorrectly (e.g. 610775162) so we just send 0...
    message.appendByte(0) # World Id
    message.appendRaw(world.name)
    return message