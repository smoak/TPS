import time

# Number of milliseconds in one minute
MS_PER_MIN = 1000

class Timer(object):
  """
  A simple timer class to keep track of 
  game time
  """

  def __init__(self):
    self.startTicks = 0
    self.pausedTicks = 0
    self.paused = False
    self.started = False

  def start(self):
    self.started = True
    self.paused = False
    self.startTicks = self.__timeMs()
    
  def stop(self):
    self.started = False
    self.paused = False

  def getTicks(self):
    if self.started:
      if self.paused:
        return self.pausedTicks
      else:
        return self.__timeMs() - self.startTicks
    # Timer isnt running
    return 0

  def pause(self):
    if self.started and not self.paused:
      self.paused = True
      self.pausedTicks = self.__timeMs() - self.startTicks
    
  def resume(self):
    if self.paused:
      self.paused = False
      self.startTicks = self.__timeMs() - self.startTicks
      self.pausedTicks = 0

  def __timeMs(self):
    """
    Helper method because time.time() returns seconds
    We care about milliseconds
    """    
    return time.time() * MS_PER_MIN
