import pygame
import pygame.freetype

from config import WHITE
from cell import Cell

OURS = 1
THEIRS = 2
LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'


def num_to_letter(num):
    return LETTERS[num]


def letter_to_num(letter):
    return LETTERS.index(letter)


class Board:

    def __init__(self, grid_size, board_type, images):
        self.font = pygame.freetype.Font(None, 28)
        self.sprites = pygame.sprite.Group()

        self.grid_size = grid_size
        self.grid = [[Cell(row, col, images) for col in range(grid_size)] for row in range(grid_size)]

        self.board_type = board_type

        for row in range(self.grid_size):
            for col in range(self.grid_size):
                cell = self.grid[row][col]
                self.sprites.add(cell)
                cell.rect.x = 30 + (col * 77)
                cell.rect.y = 30 + (row * 77)

    def make_move_click(self, x, y):
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                self.grid[row][col].make_move_click(x, y)
        self.sprites.update()

    def toggle_ship_click(self, x, y):
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                self.grid[row][col].toggle_ship_click(x, y)
        self.sprites.update()

    def check_move(self, row, col):
        self.grid[row][col].check_move()
        self.sprites.update()

    def record_hit(self, row, col):
        self.grid[row][col].record_hit()
        self.sprites.update()

    def record_miss(self, row, col):
        self.grid[row][col].record_miss()
        self.sprites.update()

    def draw(self, surface):
        for row_col in range(self.grid_size):
            self.font.render_to(surface, (58 + (row_col * 77), 5), str(row_col + 1), WHITE)
            self.font.render_to(surface, (5, 58 + (row_col * 77)), str(num_to_letter(row_col)), WHITE)

        self.sprites.draw(surface)

    def is_wiped_out(self):
        hits_to_win = 5 + 4 + 3 + 3 + 2

        hits_so_far = 0
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                if self.grid[row][col].hit:
                    hits_so_far += 1
        print("So far, there are %d hits of the needed %d to win." % (hits_so_far, hits_to_win))
        return hits_so_far >= hits_to_win

    def is_valid(self):
        # TODO: Make sure there are the five ships together.
        return True

