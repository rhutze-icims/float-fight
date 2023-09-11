from board import Board
import pytest


board = None

@pytest.fixture(autouse=True)
def run_before_and_after_tests():
    global board

    # Setup
    board = Board(3, 0, 0, None)

    yield # run test

    # Teardown


def test_horizontal_winner():
    assert board.check_for_winner() is None
    board.clear()

    board.grid[0][0].x = True
    board.grid[0][1].x = True
    board.grid[0][2].x = True
    assert board.check_for_winner() is 'X'

