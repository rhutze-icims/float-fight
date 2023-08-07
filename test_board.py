from board import Board
import pytest


board = None

@pytest.fixture(autouse=True)
def run_before_and_after_tests():
    global board

    # Setup
    mock_font = lambda family, size: None
    board = Board(mock_font, 10, 0, 0, None)

    yield # run test

    # Teardown


def test_has_enough_positions():
    assert board.has_enough_positions() is False
    for col in range(0, 5):
        board.grid[0][col].ship = True
    for col in range(0, 4):
        board.grid[1][col].ship = True
    for col in range(0, 3):
        board.grid[2][col].ship = True
        board.grid[3][col].ship = True
    for col in range(0, 2):
        board.grid[4][col].ship = True
    assert board.has_enough_positions() is True
