from config import BLACK, BLUE, DARK_BLUE, GREY
import pygame

SHADOW_SIZE = 2


class Button:

    def __init__(self, text, x_center, y_center, action=None):
        self.action = action
        self.enabled = True

        self.rect = pygame.Rect(x_center - 100, y_center - 20, 200, 40)
        self.shadow_rect = pygame.Rect(x_center - 100 + SHADOW_SIZE,
                                       y_center - 20 + SHADOW_SIZE, 200, 40)

        self.font = pygame.freetype.Font(None, 18)
        self.text = text
        self.text_rect = self.font.get_rect(self.text)

    def draw(self, surface):
        text_color = BLACK if self.enabled else GREY
        button_color = BLUE if self.enabled else DARK_BLUE

        pygame.draw.rect(surface, BLACK, self.shadow_rect)
        pygame.draw.rect(surface, button_color, self.rect)
        self.font.render_to(surface,
                (self.rect.centerx - (self.text_rect.width / 2),
                (self.rect.centery - (self.text_rect.height / 2))), None, text_color)

    def check_click(self, x, y):
        if self.action is not None and self.enabled \
                and self.rect.collidepoint(x, y):
            self.action()
            return True
        return False

    def set_enabled(self, enabled):
        self.enabled = enabled

