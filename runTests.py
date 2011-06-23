import unittest

from test import *

def runTests():
  suite = unittest.TestLoader().loadTestsFromTestCase(messageParserTest.MessageParserTest)
  unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == '__main__':
  runTests()
