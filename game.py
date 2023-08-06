from board import Board
from button import Button
from config import *
import pygame
import pygame.freetype
from pygame.color import THECOLORS
from status_bar import StatusBar


class Game:

    def __init__(self, screen, messages_to_send, our_team_id):
        self.messages_to_send = messages_to_send
        self.our_team_id = our_team_id
        self.our_game_state = STATE_PREPARING
        self.length_of_ships_to_place = [5, 4, 3, 3, 2]
        self.images = {
            'firing': pygame.image.load('missile.jpg').convert(),
            'miss': pygame.image.load('ocean.jpg').convert(),
            'hit': pygame.image.load('explosion.jpg').convert(),
            'ship': pygame.image.load('battleship.jpg').convert()
        }
        self.our_board = Board(pygame.freetype.Font, GAME_SIZE, 5, HEADER_HEIGHT, self.images)
        self.start_game_button = Button("Start", 10, 750, self.indicate_ready_to_start)

        self.status_bar = StatusBar(
            BORDER_SIZE,
            (CELL_SIZE * GAME_SIZE) + (BORDER_SIZE * 2) + HEADER_HEIGHT)
        self.status_bar.update_text('Choose your positions and click Start.')

        self.heading_bar = StatusBar(
            BORDER_SIZE,
            10)
        self.heading_bar.update_text('<-- Your Board        Opponent\'s Board -->')

        self.screen = screen
        self.their_team_id = None
        self.start_game_button.set_enabled(False)
        self.their_board = Board(pygame.freetype.Font, GAME_SIZE, 580, HEADER_HEIGHT, self.images)
        self.their_game_state = STATE_PREPARING
        self.their_team = None
        self.draw_game()

    def can_be_ready_to_start(self):
        return self.their_team_id is not None and self.our_board.is_valid()

    def indicate_ready_to_start(self):
        self.messages_to_send.put(f"{self.our_team_id}|{ACTION_READY_TO_START}|0|0")
        if self.their_game_state == STATE_READY_TO_START:
            self.start_game()
        else:
            state = STATE_READY_TO_START
            self.change_game_state(state)

    def start_game(self):
        state = STATE_OUR_TURN if self.our_team_id > self.their_team_id else STATE_THEIR_TURN
        self.change_game_state(state)

    def change_game_state(self, state):
        self.our_game_state = state
        if state == STATE_OUR_TURN:
            self.status_bar.update_text("It's your move. Good luck!")
        elif state == STATE_OUR_WIN:
            self.status_bar.update_text("Congratulations! You win!")
        elif state == STATE_READY_TO_START:
            self.status_bar.update_text("Your opponent is still preparing...")
        elif state == STATE_THEIR_WIN:
            self.status_bar.update_text("You lost. Maybe next time.")
        else:
            self.status_bar.update_text(f"Waiting for your opponent to make their move...")
        pygame.event.post(pygame.event.Event(pygame.USEREVENT, dict(action=ACTION_GAME_STATE_CHANGED, state=state)))

    def draw_game(self):
        self.screen.fill(THECOLORS['royalblue4'])
        self.our_board.draw(self.screen)
        self.status_bar.draw(self.screen)
        self.heading_bar.draw(self.screen)

        if self.our_game_state == STATE_PREPARING:
            self.start_game_button.draw(self.screen)
        elif not self.our_game_state == STATE_READY_TO_START:
            self.their_board.draw(self.screen)

    def handle_event(self, event) -> bool:
        """Decides what, if anything, to do with a received event.

        Retrieves rows pertaining to the given keys from the Table instance
        represented by table_handle.  String keys will be UTF-8 encoded.

        Args:
            event: The event, which has at least a type.

        Returns:
            True if the screen should be drawn as a result of what the event changed.
            False if the screen can stay the same as it was.
        """

        if event.type == pygame.KEYDOWN:
            print("           Down!")
            return False

        elif event.type == pygame.MOUSEMOTION:
            if self.our_board.handle_mouse_hover(event.pos[0], event.pos[1]) == HANDLED:
                return True

        elif event.type == pygame.MOUSEBUTTONUP:
            if self.our_game_state == STATE_PREPARING \
                    and self.our_board.toggle_ship_click(event.pos[0], event.pos[1]) == HANDLED:
                self.start_game_button.set_enabled(self.can_be_ready_to_start())
                return True
            else:
                if self.our_game_state == STATE_PREPARING:
                    self.start_game_button.check_click(event.pos[0], event.pos[1])
                    return True
                else:
                    self.their_board.make_move_click(event.pos[0], event.pos[1])
                    return True

        elif event.type == pygame.USEREVENT:
            if event.action == ACTION_FIND_ME:
                if not event.team_id == self.our_team_id and self.their_team_id is None:
                    self.their_team_id = event.team_id
                    print(f"          Their team ID is [ {self.their_team_id} ].")
                    self.start_game_button.set_enabled(self.can_be_ready_to_start())
                return True

            elif event.action == ACTION_HIT and event.team_id == self.their_team_id:
                self.their_board.record_hit(event.row, event.col)
                if self.their_board.is_wiped_out():
                    self.change_game_state(STATE_OUR_WIN)
                    return True
                else:
                    self.change_game_state(STATE_THEIR_TURN)
                    return True

            elif event.action == ACTION_MAKE_MOVE and self.our_game_state == STATE_OUR_TURN:
                self.their_board.record_firing(event.row, event.col)
                self.messages_to_send.put(f"{self.our_team_id}|{ACTION_MOVE}|{event.row}|{event.col}")
                return True

            elif event.action == ACTION_MISS and event.team_id == self.their_team_id:
                self.their_board.record_miss(event.row, event.col)
                self.change_game_state(STATE_THEIR_TURN)
                return True

            elif event.action == ACTION_MOVE:
                if event.team_id == self.their_team_id and self.our_board.check_move(event.row, event.col) == HANDLED:
                    if self.our_board.is_wiped_out():
                        self.change_game_state(STATE_THEIR_WIN)
                    else:
                        self.change_game_state(STATE_OUR_TURN)
                    return True

            elif event.action == ACTION_READY_TO_START:
                self.their_game_state = STATE_READY_TO_START
                if self.our_game_state == STATE_READY_TO_START:
                    self.start_game()
                    return True

            elif event.action == ACTION_STATUS:
                self.status_bar.update_text(event.text)
                return True

            elif event.action == ACTION_WE_GOT_HIT:
                self.messages_to_send.put(f"{self.our_team_id}|{ACTION_HIT}|{event.row}|{event.col}")
                return False

            elif event.action == ACTION_WE_WERE_MISSED:
                self.messages_to_send.put(f"{self.our_team_id}|{ACTION_MISS}|{event.row}|{event.col}")
                return False

        return False
