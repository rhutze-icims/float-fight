from button import Button
from config import *
import pygame
from time import time


class Teams:

    panel_x = (CELL_SIZE * GAME_SIZE) + (2 * BORDER_SIZE) + 15
    panel_y = 15 + HEADER_HEIGHT
    panel_width = (CELL_SIZE * GAME_SIZE) + BORDER_SIZE
    panel_height = (CELL_SIZE * GAME_SIZE) + BORDER_SIZE

    recent_teams = {}
    recent_team_buttons = []

    def __init__(self):
        self.rect = pygame.Rect(self.panel_x, self.panel_y, self.panel_width, self.panel_height)

    def found_team(self, team, first_move_number):
        if team not in self.recent_teams:
            print(f"Registering team [{team}]...")

            self.recent_teams[team] = {
                'first_move_number': first_move_number,
                'updated': time()
            }

            number_of_teams = len(self.recent_teams)
            button = Button(team,
                            self.panel_x + BORDER_SIZE,
                            HEADER_HEIGHT + (number_of_teams * (BUTTON_HEIGHT + BORDER_SIZE)),
                            self.select_team,
                            team)
            self.recent_team_buttons.append(button)

        self.recent_teams[team]['updated'] = time()

    def draw(self, surface):
        pygame.draw.rect(surface, LIGHT_BLUE, self.rect)

        for button in self.recent_team_buttons:
            button.draw(surface)

    def select_team(self, team):
        print(f"Selected team [{team}].")
        event = pygame.event.Event(pygame.USEREVENT, dict(
            action='SELECT_TEAM',
            team=team,
            first_move_number=self.recent_teams[team]['first_move_number']
        ))
        pygame.event.post(event)

    def check_click(self, x, y):
        for team_button in self.recent_team_buttons:
            if team_button.check_click(x, y) == HANDLED:
                for other_button in self.recent_team_buttons:
                    other_button.set_selected(False)
                team_button.set_selected(True)

