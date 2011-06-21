"""
Represents a players session.
Holds data such as the player
object, their client number,
authed, etc.
"""
class SessionBase(object):
 

  def sessionConnect(self, address, suid=None):
    self.address = address 


class Session(SessionBase):
  pass
