from board import Board
import unittest
from unittest.mock import Mock


class TestBoard(unittest.TestCase):

    def setUp(self):
        mock_font = Mock()
        self.board = Board(mock_font, 5, 0, 0, None)

    def test_is_x_column_win(self):
        self.board.grid[0][0].x = True
        self.board.grid[0][1].x = True
        self.board.grid[0][2].x = True
        self.board.grid[0][3].x = True
        self.board.grid[0][4].x = True
        self.assertEqual('x', self.board.is_win())

    def test_is_o_column_win(self):
        self.board.grid[2][0].o = True
        self.board.grid[2][1].o = True
        self.board.grid[2][2].o = True
        self.board.grid[2][3].o = True
        self.board.grid[2][4].o = True
        self.assertEqual('o', self.board.is_win())

    def test_is_not_column_win(self):
        self.board.grid[0][0].o = True
        self.board.grid[0][1].o = False
        self.board.grid[0][2].x = True
        self.board.grid[0][3].o = True
        self.board.grid[0][4].o = True
        self.assertIsNone(self.board.is_win())

    def test_is_x_row_win(self):
        self.board.grid[0][0].x = True
        self.board.grid[1][0].x = True
        self.board.grid[2][0].x = True
        self.board.grid[3][0].x = True
        self.board.grid[4][0].x = True
        self.assertEqual('x', self.board.is_win())

    def test_is_o_row_win(self):
        self.board.grid[0][0].o = True
        self.board.grid[1][0].o = True
        self.board.grid[2][0].o = True
        self.board.grid[3][0].o = True
        self.board.grid[4][0].o = True
        self.assertEqual('o', self.board.is_win())

    def test_is_not_row_win(self):
        self.board.grid[0][0].o = True
        self.board.grid[1][0].o = False
        self.board.grid[2][0].x = True
        self.board.grid[3][0].o = True
        self.board.grid[4][0].o = True
        self.assertIsNone(self.board.is_win())

    def test_diagonal_win(self):
        self.board.grid[0][0].o = True
        self.board.grid[1][1].o = True
        self.board.grid[2][2].o = True
        self.board.grid[3][3].o = True
        self.board.grid[4][4].o = True
        self.assertEqual('o', self.board.is_win())

    def test_is_not_a_tie(self):
        self.assertFalse(self.board.is_tie())

    def test_not_a_tie_if_win(self):
        for row in range(self.board.grid_size):
            for col in range(self.board.grid_size):
                self.board.grid[row][col].o = True
        self.assertFalse(self.board.is_tie())

    def test_a_tie(self):
        # Make an alternating grid with no possible winner.
        for row in range(self.board.grid_size):
            for col in range(self.board.grid_size):
                if row % 2 == 0:
                    self.board.grid[row][col].x = col % 2 == 0
                    self.board.grid[row][col].o = col % 2 != 0
                else:
                    self.board.grid[row][col].x = col % 2 != 0
                    self.board.grid[row][col].o = col % 2 == 0

            # Mess up the diagonal.
            self.board.grid[row][row].x = row % 2 == 0
            self.board.grid[row][row].o = row % 2 != 0

        print(str(self.board))

        self.assertTrue(self.board.is_tie())

if __name__ == '__main__':
    unittest.main()
