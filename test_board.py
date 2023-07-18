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


def test_is_valid():
    board.grid[0][0].ship = False
    assert board.is_valid() is False

    board.grid[0][0].ship = True
    assert board.is_valid() is True
