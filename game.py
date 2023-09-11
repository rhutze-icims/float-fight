from board import Board
from config import *
import pygame
from pygame.color import THECOLORS
from pygame.event import Event
import pygame.freetype
from status_bar import StatusBar


class Game:

    def __init__(self, screen):
        self.our_game_state = STATE_X_TURN
        self.images = {
            'X': pygame.image.load('explosion.jpg').convert(),
            'O': pygame.image.load('ocean.jpg').convert()
        }
        self.our_board = Board(GAME_SIZE, 5, HEADER_HEIGHT, self.images)

        self.game_status = StatusBar(BORDER_SIZE, (CELL_SIZE * GAME_SIZE) + (BORDER_SIZE * 2) + HEADER_HEIGHT)
        self.game_status.update_text("It's X's move. Good luck!")

        self.screen = screen
        self.draw_game()

    def draw_game(self) -> None:
        """
        Passes the pygame screen to each of the classes that need to draw part of the screen.
        """

        self.screen.fill(THECOLORS['royalblue4'])
        self.our_board.draw(self.screen)
        self.game_status.draw(self.screen)

    def handle_event(self, event: Event) -> bool:
        """
        Decides what, if anything, to do with a received event.

        Parameters:
            event: An event from pygame

        Returns:
            True if the screen should be drawn as a result of what the event changed.
            False if the screen can stay the same as it was.
        """

        if event.type == pygame.MOUSEBUTTONUP:
            self.our_board.make_move_click(event.pos[0], event.pos[1])
            return True

        elif event.type == pygame.USEREVENT:
            if event.action == ACTION_MOVE:
                if self.our_game_state == STATE_X_TURN:
                    self.our_board.record_x(event.row, event.col)
                elif self.our_game_state == STATE_O_TURN:
                    self.our_board.record_o(event.row, event.col)

                the_winner = self.our_board.check_for_winner()

                if the_winner == 'X':
                    self.our_game_state = STATE_X_WIN
                    self.game_status.update_text("X wins! Congratulations!")
                elif the_winner == 'O':
                    self.our_game_state = STATE_O_WIN
                    self.game_status.update_text("O wins! Congratulations!")
                elif self.our_game_state == STATE_X_TURN:
                    self.our_game_state = STATE_O_TURN
                    self.game_status.update_text("It's O's move. Good luck!")
                elif self.our_game_state == STATE_O_TURN:
                    self.our_game_state = STATE_X_TURN
                    self.game_status.update_text("It's X's move. Good luck!")
                return True

        # If we got this far, then this event isn't of a type that we care about. So, we'll do
        # nothing. We'll also return False, meaning that the screen does not need to redraw.
        return False
