class WorldMapper(object):
  """
  Maps L{World} and L{WorldEntity} objects
  """
  
  def domainToEntity(self, domain, entity):
    """
	  Maps a L{World} domain object to a L{WorldEntity} object
	  """
    entity.name = domain.name
    entity.time = domain.time
    entity.width = domain.width
    entity.height = domain.height
    entity.spawnX = domain.spawn[0]
    entity.spawnY = domain.spawn[1]
    entity.worldSurface = domain.worldSurface
    entity.rockLayer = domain.rockLayer
    entity.isDay = domain.isDay
    entity.isBloodMoon = domain.isBloodMoon
    entity.moonPhase = domain.moonPhase
    entity.shadowOrbSmashed = domain.shadowOrbSmashed
    entity.bossOneDowned = domain.bossOneDowned
    entity.bossTwoDowned = domain.bossTwoDowned
    entity.bossThreeDowned = domain.bossThreeDowned
    entity.leftWorld = domain.leftWorld
    entity.rightWorld = domain.rightWorld
    entity.bottomWorld = domain.bottomWorld
    entity.topWorld = domain.topWorld
    entity.version = domain.version
    entity.dungeonX = domain.dungeonX
    entity.dungeonY = domain.dungeonY
    entity.spawnMeteor = domain.spawnMeteor
    entity.shadowOrbCount = domain.shadowOrbCount
    entity.invasionDelay = domain.invasionDelay
    entity.invasionSize = domain.invasionSize
    entity.invasionType = domain.invasionType
    entity.invasionX = domain.invasionX
    
  def entityToDomain(self, entity, domain):
    """
    Maps a L{WorldEntity} to a L{World} object
    """
    domain.worldId = entity.id
    domain.name = entity.name
    domain.time = entity.time
    domain.width = entity.width
    domain.height = entity.height
    domain.spawn = (entity.spawnX, entity.spawnY)    
    domain.worldSurface = entity.worldSurface
    domain.rockLayer = entity.rockLayer
    domain.isDay = entity.isDay
    domain.isBloodMoon = entity.isBloodMoon
    domain.moonPhase = entity.moonPhase
    domain.shadowOrbSmashed = entity.shadowOrbSmashed
    domain.bossOneDowned = entity.bossOneDowned
    domain.bossTwoDowned = entity.bossTwoDowned
    domain.bossThreeDowned = entity.bossThreeDowned
    domain.leftWorld = entity.leftWorld
    domain.rightWorld = entity.rightWorld
    domain.bottomWorld = entity.bottomWorld
    domain.topWorld = entity.topWorld
    domain.version = entity.version
    domain.dungeonX = entity.dungeonX
    domain.dungeonY = entity.dungeonY
    domain.spawnMeteor = entity.spawnMeteor
    domain.shadowOrbCount = entity.shadowOrbCount
    domain.invasionDelay = entity.invasionDelay
    domain.invasionSize = entity.invasionSize
    domain.invasionType = entity.invasionType
    domain.invasionX = entity.invasionX