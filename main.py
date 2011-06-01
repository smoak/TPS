import logging
import logging.handlers

from net.server import TerrariaServer

LOG_FILENAME = "main.log"

log = logging.getLogger("main")

def main():
  # Add the log message handler to the logger
  handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=10*1024*1024, backupCount=5)
  formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
  handler.setFormatter(formatter)
  TerrariaServer.log.addHandler(handler)
  TerrariaServer.log.setLevel(logging.DEBUG)
  s = TerrariaServer("", 7777, None)
  s.start()

if __name__ == '__main__':
  main()
