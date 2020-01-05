from board import Board
import unittest
from unittest.mock import Mock


class TestBoard(unittest.TestCase):

    def setUp(self):
        mock_font = Mock()
        self.board = Board(mock_font, 10, 0, 0, None)

    def test_is_valid(self):
        self.board.grid[0][0].ship = False
        self.assertFalse(self.board.is_valid())

        self.board.grid[0][0].ship = True
        self.assertTrue(self.board.is_valid())


if __name__ == '__main__':
    unittest.main()
