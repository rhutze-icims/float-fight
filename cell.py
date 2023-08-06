from config import *
import pygame
from pygame.color import THECOLORS


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
        if self.rect.collidepoint(x, y) and not self.already_played():
            event = pygame.event.Event(pygame.USEREVENT, dict(action=ACTION_MAKE_MOVE, row=self.row, col=self.col))
            pygame.event.post(event)

    def check_move(self):
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

    def toggle_ship_click(self, x, y):
        if self.rect.collidepoint(x, y):
            self.ship = not self.ship
            return True
        else:
            return False

    def contains(self, x, y):
        return self.rect.collidepoint(x, y)

    def clear(self):
        self.firing = False
        self.ship = False
        self.hit = False
        self.miss = False

    def record_firing(self):
        self.firing = True

    def record_hit(self):
        self.firing = False
        self.hit = True

    def record_miss(self):
        self.firing = False
        self.miss = True
