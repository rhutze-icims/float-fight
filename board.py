from functools import reduce
from typing import NamedTuple

from cell import Cell
from config import *
import pygame
import pygame.freetype
from pygame.color import THECOLORS


def num_to_letter(num):
    return LETTERS[num]


def letter_to_num(letter):
    return LETTERS.index(letter)


class Board:

    def __init__(self, pygame_font, grid_size, x, y, images):
        self.font = pygame_font(None, 28)
        self.sprites = pygame.sprite.Group()

        self.board_x = x
        self.board_y = y
        self.grid_size = grid_size
        self.grid = [[Cell(row, col, images) for col in range(grid_size)] for row in range(grid_size)]

        self.ships = [Ship(5, []), Ship(4, []), Ship(3, []), Ship(3, []), Ship(2, [])]
        self.ship_drawing_index = 0
        self.ship_drawing_vertical = True

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

    def toggle_ship_click(self, x, y) -> bool:
        ship_drawing_length = 0 if self.ship_drawing_index is None else self.ships[self.ship_drawing_index].length
        if ship_drawing_length > 0:
            for row in range(self.grid_size):
                for col in range(self.grid_size):
                    self.grid[row][col].highlight = False
            clicked_cell = self.find_click_row_col(x, y)
            if clicked_cell is not None:
                ship_cells = self.calculate_ship_cells(clicked_cell[0], clicked_cell[1],
                                                       ship_drawing_length, self.ship_drawing_vertical)
                if ship_cells is not None:
                    self.ships[self.ship_drawing_index] = Ship(ship_drawing_length, ship_cells)
                    for cell in ship_cells:
                        cell.ship = True
                    if self.ship_drawing_index + 1 < len(self.ships):
                        self.ship_drawing_index += 1
                    else:
                        self.ship_drawing_index = None
                    self.sprites.update()
                    return True
        return False

    def handle_mouse_hover(self, x, y):
        ship_drawing_length = 0 if self.ship_drawing_index is None else self.ships[self.ship_drawing_index].length
        if ship_drawing_length > 0:
            for row in range(self.grid_size):
                for col in range(self.grid_size):
                    self.grid[row][col].highlight = False
            clicked_cell = self.find_click_row_col(x, y)
            if clicked_cell is not None:
                ship_cells = self.calculate_ship_cells(clicked_cell[0], clicked_cell[1],
                                                       ship_drawing_length, self.ship_drawing_vertical)
                if ship_cells is not None:
                    for cell in ship_cells:
                        cell.highlight = True
        self.sprites.update()
        return True

    def calculate_ship_cells(self, row, col, length, vertical):
        cells = []
        if vertical:
            if row + length > self.grid_size:
                return None
            for r in range(row, row + length):
                if self.grid[r][col].ship:
                    return None
                cells.append(self.grid[r][col])
        else:
            if col + length > self.grid_size:
                return None
            for c in range(col, col + length):
                if self.grid[row][c].ship:
                    return None
                cells.append(self.grid[row][c])
        return cells

    def find_click_row_col(self, x, y):
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                if self.grid[row][col].contains(x, y):
                    return [row, col]
        return None

    def check_move(self, row, col):
        if self.grid[row][col].check_move():
            self.sprites.update()
            return HANDLED
        return NOT_HANDLED

    def record_firing(self, row, col):
        self.grid[row][col].record_firing()
        self.sprites.update()

    def record_hit(self, row, col):
        self.grid[row][col].record_hit()
        self.sprites.update()

    def record_miss(self, row, col):
        self.grid[row][col].record_miss()
        self.sprites.update()

    def draw(self, surface):
        for row_col in range(self.grid_size):
            horizontal_rect = pygame.Rect(self.board_x + BORDER_SIZE + (row_col * (CELL_SIZE + 2)),
                                          self.board_y,
                                          CELL_SIZE, BORDER_SIZE)
            vertical_rect = pygame.Rect(self.board_x,
                                        self.board_y + BORDER_SIZE + (row_col * (CELL_SIZE + 2)),
                                        BORDER_SIZE, CELL_SIZE)

            horizontal_text_rect = self.font.get_rect(str(row_col + 1))
            self.font.render_to(surface,
                                (horizontal_rect.centerx - (horizontal_text_rect.width / 2),
                                (horizontal_rect.centery - (horizontal_text_rect.height / 2))),
                                str(row_col + 1), THECOLORS['white'])

            vertical_text_rect = self.font.get_rect(num_to_letter(row_col))
            self.font.render_to(surface,
                                (vertical_rect.centerx - (vertical_text_rect.width / 2),
                                (vertical_rect.centery - (vertical_text_rect.height / 2))),
                                num_to_letter(row_col), THECOLORS['white'])

        self.sprites.draw(surface)

    def is_wiped_out(self):
        hits_to_win = reduce(lambda total, ship: total + ship.length, self.ships, 0)
        hits_so_far = 0
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                if self.grid[row][col].hit:
                    hits_so_far += 1
        print(f"          So far, {hits_so_far} hit(s) of the {hits_to_win} needed to win.")
        return hits_so_far >= hits_to_win

    def rotate_drawing(self):
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                self.grid[row][col].highlight = False
        self.ship_drawing_vertical = not self.ship_drawing_vertical

    def has_enough_positions(self):
        count = 0
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                count += 1 if self.grid[row][col].ship else 0
        return count == 17


class Ship(NamedTuple):
    length: int
    cells: list[Cell]
