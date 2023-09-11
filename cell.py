from config import *
import pygame
from pygame.color import THECOLORS


# Each instance of our Cell is a pygame sprite. https://www.pygame.org/docs/ref/sprite.html
# A sprite is a piece of the screen that knows how to draw itself, knows which x and y coordinates to draw itself
# at, and knows if a mouse click's x and y coordinates touched part of that sprite or not. Sprites can also hold
# onto variables about themselves, which is how each Cell remembers if it was already used for a player's move.


class Cell(pygame.sprite.Sprite):
    x = False
    o = False
    image = None  # Which image to draw

    def __init__(self, row, col, images):
        super().__init__()

        self.row = row
        self.col = col
        self.images = images
        self.rect = pygame.Rect((0, 0), (CELL_SIZE, CELL_SIZE))
        self.update()

    def update(self):
        if self.x:
            self.image = self.images['X']
        elif self.o:
            self.image = self.images['O']
        else:
            self.image = pygame.Surface([CELL_SIZE, CELL_SIZE])
            self.image.fill(THECOLORS['black'])

    def handle_click(self, x, y):
        # Every Cell is going to hear about every mouse click. Most of the cells are going to say, "Nope, the click
        # isn't for me." and just ignore it. It is up to this code to check with pygame's collide code and speak up
        # and say "I'm the cell that got clicked!"
        if self.contains(x, y) and not self.already_played():

            # Notice how this Cell code is mostly generic and doesn't really know the rules of the game.
            # It just announces that it was clicked. It's up to the game board to figure out whose turn it
            # is and what to do about it. This same Cell could be used for a different game, like float-fight,
            # pretty easily. Also, a move could come from elsewhere, like a keyboard, or over the Internet, and
            # it would work mostly the same way.
            event = pygame.event.Event(pygame.USEREVENT, dict(action=ACTION_MOVE, row=self.row, col=self.col))
            pygame.event.post(event)


    def already_played(self):
        return self.x or self.o

    def contains(self, x, y):
        return self.rect.collidepoint(x, y)

    def clear(self):
        self.x = False
        self.o = False

    def record_x(self):
        self.x = True

    def record_o(self):
        self.o = True

