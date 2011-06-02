from net.server import TerrariaServer



def main():

  import logging.config
  logging.config.fileConfig('logging.conf')
  s = TerrariaServer("", 7777, None)
  s.start()

if __name__ == '__main__':
  main()
