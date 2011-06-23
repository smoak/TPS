import unittest

from net.messageparser import *

class MessageParserTest(unittest.TestCase):
  
  def setUp(self):
    self.parser = MessageParser()

  def test_connection_request_parser(self):
    # Arrange
    msg = "\x01Terraria9"

    # Act
    result = self.parser.parse(msg)
    
    # Assert
    self.assertEqual(result.clientVersion, "Terraria9")

