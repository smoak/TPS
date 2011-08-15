from twisted.internet.task import LoopingCall, Clock

class SimulationTime(Clock):
  """
  A mechanism for performing updates to simulations such that all
  updates occur at the same instant.

  If a L{SimulationTime.callLater} is performed, when the function
  is called, it is guaranteed that no "time" (according to
  L{SimulationTime.seconds}) will pass until the function returns.

  @ivar platformClock: A provider of
      L{twisted.internet.interfaces.IReactorTime} which will be used
      to update the model time.

  @ivar granularity: The number of times to update the model time
      per second. That is, the number of "instants" per
      second. e.g., specifying 2 would make calls to seconds()
      return 0 for 0.5 seconds, then 0.5 for 0.5 seconds, then 1 for
      0.5 seconds, and so on. This number directly represents the
      B{model} frames per second.
  """
  
  def __init__(self, granularity, platformClock):
    Clock.__init__(self)
    self.granularity = granularity
    self.platformClock = platformClock
	
  def _update(self, frames):
    """
	  Advance the simulation time by one "tick", or one over granularity.
	  """
	  self.advance(1.0 * frames / self.granularity)
	
  def start(self):
    """
	  Start the simulated advancement of time.
	  """
	  self._call = LoopingCall.withCount(self._update)
	  self._call.clock = self.platformClock
	  self._call.start(1.0 / self.granularity, now=False)
	
  def stop(self):
    """
	  Stop the simulated advancement of time. Clean up all pending calls.
	  """
	  self._call.stop()