from config import BLACK, BORDER_SIZE, CELL_SIZE, GAME_SIZE, GREY, SCREEN_WIDTH, WHITE
import pygame

class StatusBar:

    def __init__(self):
        self.font = pygame.freetype.Font(None, 18)
        self.rect = pygame.Rect(BORDER_SIZE,
                                       (CELL_SIZE * GAME_SIZE) + (BORDER_SIZE * 2),
                                       SCREEN_WIDTH - (BORDER_SIZE * 2), 30)
        self.text = ''

    def update_text(self, text):
        self.text = text

    def draw(self, surface):
        pygame.draw.rect(surface, GREY, self.rect)

        if len(self.text) > 0:
            text_rect = self.font.get_rect(self.text)
            self.font.render_to(surface,
                                (
                                    self.rect.centerx - (text_rect.width / 2),
                                    (self.rect.centery - (text_rect.height / 2))
                                ), None, BLACK)

