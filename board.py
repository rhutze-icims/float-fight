from cell import Cell
from config import *
import pygame
import pygame.freetype


class Board:

    def __init__(self, pygame_font, grid_size, x, y, images):
        self.font = pygame_font(None, 28)
        self.sprites = pygame.sprite.Group()

        self.board_x = x
        self.board_y = y
        self.grid_size = grid_size
        self.grid = [[Cell(row, col, images) for col in range(grid_size)] for row in range(grid_size)]

        for row in range(self.grid_size):
            for col in range(self.grid_size):
                cell = self.grid[row][col]
                self.sprites.add(cell)
                cell.rect.x = self.board_x + 30 + (col * (CELL_SIZE + 2))
                cell.rect.y = self.board_y + 30 + (row * (CELL_SIZE + 2))

    def make_move_click(self, x, y):
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                self.grid[row][col].make_move_click(x, y)
        self.sprites.update()

    def record_move(self, letter_of_move, row, col):
        if self.grid[row][col].record_move(letter_of_move):
            self.sprites.update()
            return HANDLED
        return NOT_HANDLED

    def draw(self, surface):
        self.sprites.draw(surface)

    def is_win(self):
        for row in range(self.grid_size):
            # Check across the columns of this row.
            tally = 0
            for col in range(self.grid_size):
                if self.grid[row][col].x:
                    tally = tally + 1
                elif self.grid[row][col].o:
                    tally = tally - 1
            if tally == self.grid_size * 1:
                return 'x'
            if tally == self.grid_size * -1:
                return 'o'

        for col in range(self.grid_size):
            # Check across the rows of this column.
            tally = 0
            for row in range(self.grid_size):
                if self.grid[row][col].x:
                    tally = tally + 1
                elif self.grid[row][col].o:
                    tally = tally - 1
            if tally == self.grid_size * 1:
                return 'x'
            if tally == self.grid_size * -1:
                return 'o'

        tally = 0
        for diag in range(self.grid_size):
            if self.grid[diag][diag].x:
                tally = tally + 1
            elif self.grid[diag][diag].o:
                tally = tally - 1
            if tally == self.grid_size * 1:
                return 'x'
            if tally == self.grid_size * -1:
                return 'o'

        return None

    def is_tie(self):
        if self.is_win():
            return False
        # If there are zero spots left.
        tally = 0
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                if not self.grid[row][col].x and not self.grid[row][col].o:
                    tally = tally + 1
        return tally == 0

    def clear_all_cells(self):
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                self.grid[row][col].clear()

    def __str__(self):
        output = ""
        for row in range(self.grid_size):
            output += "\n"
            for col in range(self.grid_size):
                if self.grid[row][col].x:
                    output += " X "
                elif self.grid[row][col].o:
                    output += " O "
                else:
                    output += " . "
        return output

