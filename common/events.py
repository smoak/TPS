class EventHook(object):
  """
  A simple event hook for classes to use
  to 'fire' events
  """
  def __init__(self):
    self.__handlers = []

  def addHandler(self, handler):
    self.__handlers.append(handler)

  def removeHandler(self, handler):
    self.__handlers.remove(handler)

  def fire(self, *args, **kwargs):
    for handler in self.__handlers:
      handler(*args, **kwargs)

  def clearObjectHandlers(self, inObject):
    for theHandler in self.__handlers:
      if theHandler.im_self == inObject:
        self.removeHandler(theHandler)


class ItemCreatedEventArgs(object):
  """
  Event arguments for an item created event
  """
  def __init__(self, item, itemNumber):
    self.item = item
    self.itemNumber = itemNumber