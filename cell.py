from config import *
import pygame
from pygame.color import THECOLORS


# Each instance of our Cell is a pygame sprite. https://www.pygame.org/docs/ref/sprite.html
# A sprite is a piece of the screen that knows how to draw itself, knows which x and y coordinates to draw itself
# at, and knows if a mouse click's x and y coordinates touched part of that sprite or not. Sprites can also hold
# onto variables about themselves, which is how each Cell remembers if it was hit or not.


class Cell(pygame.sprite.Sprite):
    firing = False  # We're firing here
    highlight = False # Highlighted when planning ship placement
    hit = False  # What we hear back from our opponent
    miss = False  # What we hear back from our opponent
    ship = False  # Keep track of our own ships
    image = None  # Which image to draw

    def __init__(self, row, col, images):
        super().__init__()

        self.row = row
        self.col = col
        self.images = images
        self.rect = pygame.Rect((0, 0), (CELL_SIZE, CELL_SIZE))
        self.update()

    def update(self):
        if self.hit:
            self.image = self.images['hit']
        elif self.ship:
            self.image = self.images['ship']
        elif self.miss:
            self.image = self.images['miss']
        elif self.firing:
            self.image = self.images['firing']
        elif self.highlight:
            self.image = pygame.Surface([CELL_SIZE, CELL_SIZE])
            self.image.fill(THECOLORS['royalblue'])
        else:
            self.image = pygame.Surface([CELL_SIZE, CELL_SIZE])
            self.image.fill(THECOLORS['black'])

    def make_move_click(self, x, y):
        # Every Cell is going to hear about every mouse click. Most of the cells are going to say, "Nope, the click
        # isn't for me." and just ignore it. It is up to this code to check with pygame's collide code and speak up
        # and say "I'm the cell that got clicked, and I'll tell our opponent that we made a move!"
        if self.contains(x, y) and not self.already_played():
            event = pygame.event.Event(pygame.USEREVENT, dict(action=ACTION_MAKE_MOVE, row=self.row, col=self.col))
            pygame.event.post(event)

    def check_move(self):
        # This is the code that gets run when our opponent made a move and we need to figure out if it was a hit or
        # a miss. Only the cell that the opponent guessed is going to have its check_move function called. If that
        # cell has ship == True, then we announce a hit event. If ship == False, then we announce a miss event.

        if self.already_played():
            print('Cell [%d, %d] was already played.' % (self.row, self.col))
            return NOT_HANDLED

        if self.ship:
            self.hit = True
            event = pygame.event.Event(pygame.USEREVENT, dict(action=ACTION_WE_GOT_HIT,  row=self.row, col=self.col))
            pygame.event.post(event)
        else:
            self.miss = True
            event = pygame.event.Event(pygame.USEREVENT, dict(action=ACTION_WE_WERE_MISSED, row=self.row, col=self.col))
            pygame.event.post(event)
        return HANDLED

    def already_played(self):
        return self.hit or self.miss

    def contains(self, x, y):
        return self.rect.collidepoint(x, y)

    def clear(self):
        self.firing = False
        self.ship = False
        self.hit = False
        self.miss = False

    def record_firing(self):
        # This function is how the board tells this cell that it should show a missle until we hear back about
        # whether the move was a hit or a miss.
        self.firing = True

    def record_hit(self):
        # This function is how the board tells this cell that it should become a hit.
        self.firing = False
        self.hit = True

    def record_miss(self):
        # This function is how the board tells this cell that it should become a miss.
        self.firing = False
        self.miss = True
