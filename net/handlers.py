import logging, types

from twisted.internet.defer import Deferred, maybeDeferred, fail
from twisted.internet.threads import deferToThread

#from net.protocols import IMessageHandler

logger = logging.getLogger()

class MessageHandlerLocator:
  handlerLookup = {}
  messageHandler = None

  def locateHandler(self, message):
#    logger.debug("Locating handler for message %r" % (message,))
    messageClass = message.__class__
    try:
      handlerFunc = self.handlerLookup[messageClass]
    except KeyError:
      return None
    handlerMethod = types.MethodType(handlerFunc, self.messageHandler)
    return deferToThread(handlerMethod, message)
