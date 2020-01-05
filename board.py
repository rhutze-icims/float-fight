from cell import Cell
from config import *
import pygame
import pygame.freetype


def num_to_letter(num):
    return LETTERS[num]


def letter_to_num(letter):
    return LETTERS.index(letter)


class Board:

    def __init__(self, grid_size, x, y, images):
        self.font = pygame.freetype.Font(None, 28)
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

    def toggle_ship_click(self, x, y):
        ship_toggled = False
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                if self.grid[row][col].toggle_ship_click(x, y):
                    ship_toggled = True
        self.sprites.update()
        return ship_toggled

    def check_move(self, row, col):
        if self.grid[row][col].check_move():
            self.sprites.update()
            return HANDLED
        return NOT_HANDLED

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
                                str(row_col + 1), WHITE)

            vertical_text_rect = self.font.get_rect(num_to_letter(row_col))
            self.font.render_to(surface,
                                (vertical_rect.centerx - (vertical_text_rect.width / 2),
                                (vertical_rect.centery - (vertical_text_rect.height / 2))),
                                num_to_letter(row_col), WHITE)

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
        # return True
        return self.grid[0][0].ship

    def clear_all_cells(self):
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                self.grid[row][col].clear()

    def save_positions_to_file(self):
        with open('positions.txt', 'w') as file:
            for row in range(self.grid_size):
                for col in range(self.grid_size):
                    if self.grid[row][col].ship:
                        file.write(str(row) + ',' + str(col) + '\n')
        event = pygame.event.Event(
            pygame.USEREVENT, dict(action=ACTION_STATUS, text='Positions saved to [positions.txt]'))
        pygame.event.post(event)

    def load_positions_from_file(self):
        with open('positions.txt', 'r') as file:
            self.clear_all_cells()
            line = file.readline()
            while line:
                loaded_position = line.split(',')
                self.grid[int(loaded_position[0])][int(loaded_position[1])].ship = True
                line = file.readline()
        self.sprites.update()

