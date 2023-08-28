from functools import reduce
from typing import NamedTuple

from cell import Cell
from config import *
import pygame
import pygame.freetype
from pygame.color import THECOLORS


# Python arrays identify each slot using number, not a letter. Our game board identifies each row and column using
# a letting, not a number. The num_to_letter and letter_to_num functions help other parts of the code to easily
# switch back and forth between the two.

def num_to_letter(num):
    return LETTERS[num]


def letter_to_num(letter):
    return LETTERS.index(letter)


class Board:

    def __init__(self, pygame_font, grid_size, x, y, images):
        self.font = pygame_font(None, 28)

        # We'll add all of the board's cells to this group. That way, we can tell pygame to do things to all of
        # the cells at the same time. For example, self.cell_group.update() will redraw all of them.
        self.cell_group = pygame.sprite.Group()

        self.board_x = x
        self.board_y = y
        self.grid_size = grid_size
        self.grid = [[Cell(row, col, images) for col in range(grid_size)] for row in range(grid_size)]

        # A Ship class has a length and an array of cells. "ships" is an array with the five ships in it.
        # The array of cells starts off empty, until the player decides where the ship is positioned.
        self.ships = [Ship(5, []), Ship(4, []), Ship(3, []), Ship(3, []), Ship(2, [])]

        # Which ship in the array are we drawing right now?
        # Arrays are 0-based, so 0 means the first ship in the ships array. We'll go from 0 to 4.
        # If this is None, we're done drawing ships.
        self.ship_drawing_index = 0

        # When ship_drawing_vertical is true, the user wants to draw the next ship vertically. When it's false,
        # then horizontally.
        self.ship_drawing_vertical = True

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
                self.grid[row][col].make_move_click(x, y)
        self.cell_group.update()

    def toggle_ship_click(self, x, y) -> bool:
        ship_drawing_length = 0 if self.ship_drawing_index is None else self.ships[self.ship_drawing_index].length
        if ship_drawing_length > 0:
            for row in range(self.grid_size):
                for col in range(self.grid_size):
                    self.grid[row][col].highlight = False
            clicked_row_col = self.from_mouse_coord_to_grid_row_col(x, y)
            if clicked_row_col is not None:
                ship_cells = self.calculate_ship_cells(clicked_row_col[0], clicked_row_col[1],
                                                       ship_drawing_length, self.ship_drawing_vertical)
                if ship_cells is not None:
                    self.ships[self.ship_drawing_index] = Ship(ship_drawing_length, ship_cells)
                    for cell in ship_cells:
                        cell.ship = True
                    if self.ship_drawing_index + 1 < len(self.ships):
                        self.ship_drawing_index += 1
                    else:
                        self.ship_drawing_index = None
                    self.cell_group.update()
                    return True
        return False

    # When positioning the ships, this function notes where the mouse is hovering and highlights the cells where
    # the ship would go if the user clicks.
    def handle_mouse_hover(self, x, y):
        # Decide how many consecutive cells to highlight. If we're not supposed to be drawing ships right now,
        # this will be 0, so nothing happens.
        ship_drawing_length = 0 if self.ship_drawing_index is None else self.ships[self.ship_drawing_index].length

        # Are we trying to draw a ship right now?
        if ship_drawing_length > 0:

            # We ARE trying to draw a ship right. First, let's tell the cells to get rid of any old highlights.
            for row in range(self.grid_size):
                for col in range(self.grid_size):
                    self.grid[row][col].highlight = False

            mouse_hovering_cell = self.from_mouse_coord_to_grid_row_col(x, y)
            if mouse_hovering_cell is not None:

                # Could the current ship fit in this spot? It's not bumping into the edge or another ship, right?
                ship_cells = self.calculate_ship_cells(mouse_hovering_cell[0], mouse_hovering_cell[1],
                                                       ship_drawing_length, self.ship_drawing_vertical)
                # Looks like it can fit. Tell the cells, that would be part of this ship, to highlight themselves.
                if ship_cells is not None:
                    for cell in ship_cells:
                        cell.highlight = True

        # Tell all of the cells to redraw themselves.
        self.cell_group.update()
        return True

    # Figure out which cells a ship would take up. We know which row and column it wants to start at.
    # We know how long the ship would be and if it should be vertical or horizontal.
    # Returning None means the ship wouldn't fit. Otherwise, we'll return an array of which cells should be used.
    def calculate_ship_cells(self, row, col, length, vertical):
        cells = []
        if vertical:
            if row + length > self.grid_size:
                # The vertical ship would go past the end of the row.
                return None
            for r in range(row, row + length):
                if self.grid[r][col].ship:
                    # One of the cells is already another ship.
                    return None
                # If we got this far, we can safely add this cell to the array.
                cells.append(self.grid[r][col])
        else:
            if col + length > self.grid_size:
                # The horizontal ship would go past the end of the column.
                return None
            for c in range(col, col + length):
                if self.grid[row][c].ship:
                    # One of the cells is already another ship.
                    return None
                # If we got this far, we can safely add this cell to the array.
                cells.append(self.grid[row][c])
        return cells

    def from_mouse_coord_to_grid_row_col(self, x, y):
        # Iterate through each row.
        for row in range(self.grid_size):
            # Within each row, iterate through each column.
            for col in range(self.grid_size):
                # For each cell, if it is the one that was clicked, return that row and column.
                # Otherwise, keep looking.
                if self.grid[row][col].contains(x, y):
                    return [row, col]
        # If we got this far without returning, it looks like the mouse click wasn't on any of the cells.
        return None

    def check_move(self, row, col):
        if self.grid[row][col].check_move():
            self.cell_group.update()
            return HANDLED
        return NOT_HANDLED

    def record_firing(self, row, col):
        # Tells the cell at that row and column that it is where a move was made and that it should change its
        # variables and which image it is showing.
        self.grid[row][col].record_firing()
        self.cell_group.update()

    def record_hit(self, row, col):
        # Same as record_firing, but tells the cell that it should consider itself hit.
        self.grid[row][col].record_hit()
        self.cell_group.update()

    def record_miss(self, row, col):
        # Same as record_firing, but tells the cell that it should consider itself missed.
        self.grid[row][col].record_miss()
        self.cell_group.update()

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

        self.cell_group.draw(surface)

    def is_every_position_hit(self) -> bool:
        # Ask each ship in self.ships how many cells it takes up. Count them all up into hits_to_win
        # Python's "reduce" is a clever way to do all of that in one line of code! But, it's just doing the
        # same thing as the code a few lines down that, instead of counting the ships, is counting the hits.
        hits_to_win = reduce(lambda total, ship: total + ship.length, self.ships, 0)

        # Now we're going to count the hits. We'll start counting at 0.
        hits_so_far = 0

        for row in range(self.grid_size):
            for col in range(self.grid_size):
                if self.grid[row][col].hit:
                    hits_so_far += 1

        print(f"          So far, {hits_so_far} hit(s) of the {hits_to_win} needed to win.")
        # This returns true if the number of hits reached the number of cells.
        return hits_so_far >= hits_to_win

    def rotate_ship_drawing(self) -> None:
        """
        When hovering the mouse over cells to decide where ships to be placed,
        ship_drawing_vertical decides if the ship should be horizontal or vertical.
        This function toggles ship_drawing_vertical between the two modes. And just in case,
        it gets rid of any ship highlights that were already showing from the old mode.
        """
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                self.grid[row][col].highlight = False
        self.ship_drawing_vertical = not self.ship_drawing_vertical

    def has_enough_positions(self) -> bool:
        """
        Before our side is ready to start, all of our ships must be added to the board.
        A clever way to figure that out is to count up how many cells have a ship in them.

        Returns:
            True if the expected number of cells have ships in them.
        """
        ship_position_count = reduce(lambda total, ship: total + ship.length, self.ships, 0)
        count = 0
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                count += 1 if self.grid[row][col].ship else 0
        return count == ship_position_count


class Ship(NamedTuple):
    length: int
    cells: list[Cell]
