from net.message import *

class MessageBuilder(object):

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
