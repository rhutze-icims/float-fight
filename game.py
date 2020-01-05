from board import Board
from button import Button
from config import *
import pygame
from status_bar import StatusBar
from teams import Teams


class Game:

    def __init__(self, screen, messages_to_send, our_team, our_team_first_move):
        self.game_state = STATE_PREPARING
        self.images = {
            'ocean': pygame.image.load('ocean.jpg').convert(),
            'explosion': pygame.image.load('explosion.jpg').convert(),
            'ship': pygame.image.load('battleship.jpg').convert()
        }
        self.our_board = Board(GAME_SIZE, 5, 0, self.images)

        self.load_positions_button = Button("Load", 10, 750, self.our_board.load_positions_from_file)
        self.messages_to_send = messages_to_send
        self.our_team = our_team
        self.our_team_first_move = our_team_first_move
        self.save_positions_button = Button("Save", 70, 750, self.our_board.save_positions_to_file)
        self.start_game_button = Button("Start", 130, 750, self.start_game)
        self.status_bar = StatusBar()
        self.screen = screen
        self.selected_their_team = None
        self.selected_their_team_first_move = None
        self.start_game_button.set_enabled(False)
        self.status_bar.update_text('Choose your positions, an opponent, and click Start.')
        self.teams = Teams()
        self.their_board = Board(GAME_SIZE, 580, 0, self.images)
        self.their_team = None

    def can_start_game(self):
        return self.selected_their_team is not None and self.our_board.is_valid()

    def start_game(self):
        self.their_team = self.selected_their_team
        state = STATE_OUR_TURN if self.our_team_first_move > self.selected_their_team_first_move else STATE_THEIR_TURN
        self.change_game_state(state)

    def change_game_state(self, state):
        self.game_state = state
        if state == STATE_OUR_TURN:
            self.status_bar.update_text("It's your move. Good luck!")
        elif state == STATE_OUR_WIN:
            self.status_bar.update_text("Congratulations! You win!")
        elif state == STATE_THEIR_WIN:
            self.status_bar.update_text("You lost. Maybe next time.")
        else:
            self.status_bar.update_text('Waiting for %s to make their move...' % self.their_team)
        pygame.event.post(pygame.event.Event(pygame.USEREVENT, dict(action='GAME_STATE_CHANGED', state=state)))

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            print("Down!")

        elif event.type == pygame.MOUSEBUTTONUP:
            if self.save_positions_button.check_click(event.pos[0], event.pos[1]) == HANDLED:
                pass
            elif self.load_positions_button.check_click(event.pos[0], event.pos[1]) == HANDLED:
                pass
            elif self.game_state == STATE_PREPARING \
                    and self.our_board.toggle_ship_click(event.pos[0], event.pos[1]) == HANDLED:
                self.start_game_button.set_enabled(self.can_start_game())
            else:
                if self.game_state == STATE_PREPARING:
                    self.teams.check_click(event.pos[0], event.pos[1])
                    self.start_game_button.check_click(event.pos[0], event.pos[1])
                else:
                    self.their_board.make_move_click(event.pos[0], event.pos[1])

        elif event.type == pygame.USEREVENT:
            if event.action == 'FIND_ME':
                if not event.team == self.our_team:
                    self.teams.found_team(event.team, event.row)

            elif event.action == 'HIT' and event.team == self.their_team:
                self.their_board.record_hit(event.row, event.col)
                if self.their_board.is_wiped_out():
                    self.change_game_state(STATE_OUR_WIN)

            elif event.action == 'MAKE-MOVE' and self.game_state == STATE_OUR_TURN:
                self.messages_to_send.put('%s|MOVE|%d|%d' % (self.our_team, event.row, event.col))
                self.change_game_state(STATE_THEIR_TURN)

            elif event.action == 'MISS' and event.team == self.their_team:
                self.their_board.record_miss(event.row, event.col)

            elif event.action == 'MOVE':
                if event.team == self.their_team and self.our_board.check_move(event.row, event.col) == HANDLED:
                    if self.our_board.is_wiped_out():
                        self.change_game_state(STATE_THEIR_WIN)
                    else:
                        self.change_game_state(STATE_OUR_TURN)

            elif event.action == 'SELECT_TEAM':
                self.selected_their_team = event.team
                self.selected_their_team_first_move = event.first_move_number
                self.start_game_button.set_enabled(self.can_start_game())

            elif event.action == 'STATUS':
                self.status_bar.update_text(event.text)

            elif event.action == 'WE-GOT-HIT':
                self.messages_to_send.put('%s|HIT|%d|%d' % (self.our_team, event.row, event.col))

            elif event.action == 'WE-WERE-MISSED':
                self.messages_to_send.put('%s|MISS|%d|%d' % (self.our_team, event.row, event.col))

        self.screen.fill(DARK_BLUE)
        self.our_board.draw(self.screen)
        self.status_bar.draw(self.screen)

        if self.game_state == STATE_PREPARING:
            self.save_positions_button.draw(self.screen)
            self.load_positions_button.draw(self.screen)
            self.start_game_button.draw(self.screen)
            self.teams.draw(self.screen)
        else:
            self.their_board.draw(self.screen)

