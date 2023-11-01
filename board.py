import config
from cell import Cell
from config import *
import pygame


class Board:

    def __init__(self, grid_size, x, y, images):
        # We'll add all of the board's cells to this group. That way, we can tell pygame to do things to all of
        # the cells at the same time. For example, self.cell_group.update() will redraw all of them.
        self.cell_group = pygame.sprite.Group()

        self.board_x = x
        self.board_y = y
        self.grid_size = grid_size

        # The grid is an array of rows. Then, each row has an array of columns in it.
        self.grid = []
        for row_number in range(grid_size):
            row_of_columns = []
            for col_number in range(grid_size):
                row_of_columns.append(Cell(row_number, col_number, images))
            self.grid.append(row_of_columns)

        # Python has a fancy way of building the grid in one line, but it's also hard to read.
        #self.grid = [[Cell(row, col, images) for col in range(grid_size)] for row in range(grid_size)]


        for row in range(self.grid_size):
            for col in range(self.grid_size):
                cell = self.grid[row][col]
                # Add the cell to a group. Later, we'll use the group to easily talk to every cell at the same time.
                self.cell_group.add(cell)
                # Tell each cell where it should place itself on the screen.
                cell.rect.x = self.board_x + 30 + (col * (CELL_SIZE + 2))
                cell.rect.y = self.board_y + 30 + (row * (CELL_SIZE + 2))

    # Tell every cell in the grid about where a mouse click happened. Most cells will ignore this but the cell that
    # decides it is the one that was clicked will decide what to do, change its state, and make an announcement with
    # an event.
    def make_move_click(self, x, y):
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                self.grid[row][col].handle_click(x, y)
        self.cell_group.update()

    def clear(self):
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                self.grid[row][col].clear()
        self.cell_group.update()

    def record_x(self, row, col):
        self.grid[row][col].record_x()
        self.cell_group.update()

    def record_o(self, row, col):
        self.grid[row][col].record_o()
        self.cell_group.update()

    def draw(self, surface):
        self.cell_group.draw(surface)

    def check_for_winner(self) -> str:
        winning_combos = [
            [ [0,0], [1,0], [2,0] ], # Column 0 down
            [ [0,1], [1,1], [2,1] ], # Column 1 down
            [ [0,2], [1,2], [2,2] ], # Column 2 down
            [ [0,0], [0,1], [0,2] ], # Row 0 across
            [ [1,0], [1,1], [1,2] ], # Row 1 across
            [ [2,0], [2,1], [2,2] ], # Row 2 across
        ]

        # TODO: Is something missing above?

        for combo in winning_combos:
            first_cell = self.grid [combo[0][0]] [combo[0][1]]
            second_cell = self.grid [combo[1][0]] [combo[1][1]]
            third_cell = self.grid [combo[2][0]] [combo[2][1]]

            if first_cell.x is True and second_cell.x is True and third_cell.x is True:
                return 'X'
            if first_cell.o is True and second_cell.o is True and third_cell.o is True:
                return 'O'

        return None

