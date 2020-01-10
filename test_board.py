from board import Board
import unittest
from unittest.mock import Mock


class TestBoard(unittest.TestCase):

    def setUp(self):
        mock_font = Mock()
        self.board = Board(mock_font, 5, 0, 0, None)

    def test_is_our_win(self):
        self.board.grid[0][0].x = True
        self.board.grid[0][1].x = False
        self.assertFalse(self.board.is_our_win())


if __name__ == '__main__':
    unittest.main()
