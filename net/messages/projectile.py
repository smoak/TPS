from net.message import MessageType
from message import BaseMessage

class ProjectileMessage(BaseMessage):
  def __init__(self):
    BaseMessage.__init__(self)
    self.messageType = MessageType.Projectile
    self.projectile = None
  
  def create(self):
    self.writeInt32(self.messageType)
    self.writeInt16(self.projectile.identity)
    self.writeFloat(self.projectile.position[0])
    self.writeFloat(self.projectile.position[1])
    self.writeFloat(self.projectile.velocity[0])
    self.writeFloat(self.projectile.velocity[1])
    self.writeFloat(self.projectile.knockBack)
    self.writeFloat(self.projectile.damage)
    self.writeByte(self.projectile.owner)
    self.writeByte(self.projectile.projectileType)
    for ai in self.projectile.ai:
      self.writeFloat(ai)
    return BaseMessage.create(self)