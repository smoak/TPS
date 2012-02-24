import sys, getopt


from game.services import WorldService
from db.repositories import WorldRepository
from db.adapters import DatabaseAdapter
from config.database import SimpleDatabaseConfig
from game.world import World

def usage():
  print "Terraria World Importer"
  print "Usage: world_importer.py [OPTIONS]"
  print ""
  print "Options:"
  print ""
  print "--dbtype\tThe database type. Valid types: sqlite, mysql, postgresql, oracle, mssql"
  print ""
  print "--dbname\tThe database name to import into.If dbtype is sqlite then this should be the relative path to the database file"
  print ""
  print "--dbuser\t(OPTIONAL) The user to connect to the database as. Not used for sqlite"
  print ""
  print "--dbpass\t(OPTIONAL) The password used to connect to the database. Not used for sqlite"
  print ""
  print "--dbhost\t(OPTIONAL) The host name of the database server. Not used for sqlite"
  print ""
  print "--dbport\t(OPTIONAL) The port of the database server. Not used for sqlite"

def importWorldFile(worldfile, c):
  w = World()
  
  
  
def main():
  try:
    opts, args = getopt.getopt(sys.argv[1:], "hx", ["help", "dbtype=", "dbname=", "dbuser=", "dbpass=", "dbhost=", "dbport=", "worldfile="])
  except getopt.GetoptError, err:
    # print help information and exit:
    print str(err) # will print something like "option -a not recognized"
    usage()
    sys.exit(2)
  dbType = None
  dbName = None
  dbUser = None
  dbHost = None
  dbPass = None
  dbPort = None
  worldfile = None
  for o, a in opts:
    if o == "--dbtype":
      dbType = a
    elif o == "--dbname":
      dbName = a
    elif o == "--dbuser":
      dbUser = a
    elif o == "--dbpass":
      dbPass = a
    elif o == "--dbport":
      dbPort = a
    elif o == "--worldfile=":
      worldfile = a
    elif o in ("-h", "--help"):
      usage()
      sys.exit()
    else:
      assert False, "unhandled option"
  c = SimpleDatabaseConfig(dbType, dbName, userName, dbPass, dbHost, dbPort)
  importWorldFile(worldfile, c)

if __name__ == "__main__":
  main()