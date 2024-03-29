from config import *
from pygame.color import THECOLORS
import math
import pygame

SHADOW_SIZE = 2


class Button:

    def __init__(self, text, left, top, action=None, action_value=None):
        self.action = action
        self.action_value = action_value
        self.enabled = True
        self.selected = False

        self.font = pygame.freetype.Font(None, 18)
        self.text = text
        self.text_rect = self.font.get_rect(self.text)

        button_width = math.ceil(self.text_rect.width / 50) * 50
        self.rect = pygame.Rect(left, top, button_width, BUTTON_HEIGHT)
        self.shadow_rect = pygame.Rect(left + SHADOW_SIZE, top + SHADOW_SIZE, button_width, BUTTON_HEIGHT)

    def draw(self, surface):
        if self.enabled:
            text_color = THECOLORS['white']
            button_color = THECOLORS['royalblue']
        else:
            text_color = THECOLORS['gray50']
            button_color = THECOLORS['gray80']

        pygame.draw.rect(surface, THECOLORS['black'], self.shadow_rect)
        pygame.draw.rect(surface, button_color, self.rect)

        self.font.render_to(surface, (self.rect.centerx - (self.text_rect.width / 2),
                            (self.rect.centery - (self.text_rect.height / 2))), self.text, text_color)

    def check_click(self, x, y):
        if self.action is not None and self.enabled and self.rect.collidepoint(x, y):
            if self.action_value:
                self.action(self.action_value)
            else:
                self.action()
            return HANDLED
        return NOT_HANDLED

    def set_enabled(self, enabled):
        self.enabled = enabled
