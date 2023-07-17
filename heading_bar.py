from config import *
import pygame

class HeadingBar:

    def __init__(self):
        self.font = pygame.freetype.Font(None, 18)
        self.rect = pygame.Rect(BORDER_SIZE,
                                10,
                                SCREEN_WIDTH - (BORDER_SIZE * 2),
                                30)
        self.text = '<-- Your Board      Opponent\'s Board -->'

    def update_text(self, text):
        self.text = text

    def draw(self, surface):
        pygame.draw.rect(surface, GREY, self.rect)

        if len(self.text) > 0:
            text_rect = self.font.get_rect(self.text)
            self.font.render_to(surface, (self.rect.centerx - (text_rect.width / 2),
                                          (self.rect.centery - (text_rect.height / 2))), self.text, BLACK)

