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

    def is_our_win(self):
        return False

    def is_their_win(self):
        return False

    def is_tie(self):
        return False

    def clear_all_cells(self):
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                self.grid[row][col].clear()

