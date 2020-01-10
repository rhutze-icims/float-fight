from config import *
import pygame


class Cell(pygame.sprite.Sprite):
    o = False  # What we hear from them
    x = False  # What we hear from them
    image = None  # Which image to draw

    def __init__(self, row, col, images):
        super().__init__()

        self.row = row
        self.col = col
        self.images = images
        self.rect = pygame.Rect((0, 0), (CELL_SIZE, CELL_SIZE))
        self.update()

    def update(self):
        if self.o:
            self.image = self.images['o']
        elif self.x:
            self.image = self.images['x']
        else:
            self.image = pygame.Surface([CELL_SIZE, CELL_SIZE])
            self.image.fill((0, 0, 0))

    def make_move_click(self, x, y):
        if self.rect.collidepoint(x, y) and not self.already_played():
            event = pygame.event.Event(pygame.USEREVENT, dict(action=ACTION_MAKE_MOVE, row=self.row, col=self.col))
            pygame.event.post(event)

    def record_move(self, letter_of_move):
        if self.already_played():
            print('Cell [%d, %d] was already played.' % (self.row, self.col))
            return NOT_HANDLED

        if letter_of_move == 'x':
            self.x = True
        else:
            self.o = True
        return HANDLED

    def already_played(self):
        return self.x or self.o

    def clear(self):
        self.x = False
        self.o = False

