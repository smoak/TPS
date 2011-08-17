from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, Boolean

Base = declarative_base()

class WorldEntity(Base):
  """
  Represents an entry in the World table
  """

  __tablename__ = "World"

  id = Column(Integer, primary_key=True)
  name = Column(String)
  time = Column(Integer)
  width = Column(Integer)
  height = Column(Integer)
  spawnX = Column(Integer)
  spawnY = Column(Integer)
  worldSurface = Column(Float)
  rockLayer = Column(Float)
  isDay = Column(Boolean)
  isBloodMoon = Column(Boolean)
  moonPhase = Column(Integer)
  shadowOrbSmashed = Column(Boolean)
  bossOneDowned = Column(Boolean)
  bossTwoDowned = Column(Boolean)
  bossThreeDowned = Column(Boolean)
  leftWorld = Column(Integer)
  rightWorld = Column(Integer)
  bottomWorld = Column(Integer)
  topWorld = Column(Integer)
  version = Column(Integer)
  dungeonX = Column(Integer)
  dungeonY = Column(Integer)
  spawnMeteor = Column(Boolean)
  shadowOrbCount = Column(Integer)
  invasionDelay = Column(Integer)
  invasionSize = Column(Integer)
  invasionType = Column(Integer)
  invasionX = Column(Float)

  def __repr__(self):
    return "<WorldEntity('%d', '%s', '%dx%d')>" % (self.id, self.name, self.width, self.height)
