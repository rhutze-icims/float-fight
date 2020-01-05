import pygame
import queue
from random import randint
import signal
import sys

from board import Board, OURS, THEIRS
from button import Button
from config import *
from network import Network
from status_bar import StatusBar
from teams import Teams

shutdown_signal = False

if len(sys.argv) < 2 or len(sys.argv[1]) > 20:
    print("\nProvide your team name of up to 20 characters when starting the application.\nExample: python main.py \"My Team Name\"\n")
    sys.exit(1)
our_team = sys.argv[1]
our_team_first_move = randint(0, 1000)

their_team = None
selected_their_team = None
selected_their_team_first_move = None

# if our_team == "A":
#     their_team = "B"
# else:
#     their_team = "A"

pygame.init()
pygame.display.set_caption('Float Fight - %s' % our_team)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

clock = pygame.time.Clock()
images = {
    'ocean': pygame.image.load('ocean.jpg').convert(),
    'explosion': pygame.image.load('explosion.jpg').convert(),
    'ship': pygame.image.load('battleship.jpg').convert()
}


def can_start_game():
    return selected_their_team is not None and our_board.is_valid()


def start_game():
    global game_state, their_team

    # Is the opponent team selected?
    # Are our ships set fairly?
    game_state = STATE_OUR_TURN if our_team_first_move > selected_their_team_first_move else STATE_THEIR_TURN
    their_team = selected_their_team
    network.update_game_state(game_state)
    prepare_turn()


def prepare_turn():
    global their_team

    if game_state == STATE_OUR_TURN:
        status_bar.update_text('It\'s your move. Good luck!')
    else:
        status_bar.update_text('Waiting for %s to make their move...' % their_team)


def handle_sigint(sig, frame):
    global shutdown_signal

    print('Received Ctrl+C. Shutting down...')
    shutdown_signal = True


signal.signal(signal.SIGINT, handle_sigint)

outbound_message_queue = queue.Queue()
our_board = Board(GAME_SIZE, 5, 0, OURS, images)
their_board = Board(GAME_SIZE, 580, 0, THEIRS, images)
status_bar = StatusBar()
teams = Teams()

load_positions_button = Button("Load", 10, 750, our_board.load_positions_from_file)
save_positions_button = Button("Save", 70, 750, our_board.save_positions_to_file)
start_game_button = Button("Start", 130, 750, start_game)
start_game_button.set_enabled(False)

network = Network(outbound_message_queue, our_team, our_team_first_move)
receiving_thread = network.start_receiving()
sending_thread = network.start_sending()

status_bar.update_text('Choose your positions, an opponent, and click Start.')
game_state = STATE_PREPARING

while not shutdown_signal:

    for received_event in pygame.event.get():
        if received_event.type == pygame.QUIT:
            shutdown_signal = True

        elif received_event.type == pygame.KEYDOWN:
            print("Down!")

        elif received_event.type == pygame.MOUSEBUTTONUP:
            if save_positions_button.check_click(received_event.pos[0], received_event.pos[1]):
                pass
            elif load_positions_button.check_click(received_event.pos[0], received_event.pos[1]):
                pass
            elif game_state == STATE_PREPARING and our_board.toggle_ship_click(received_event.pos[0], received_event.pos[1]):
                start_game_button.set_enabled(can_start_game())
            else:
                if game_state == STATE_PREPARING:
                    teams.check_click(received_event.pos[0], received_event.pos[1])
                    start_game_button.check_click(received_event.pos[0], received_event.pos[1])
                else:
                    their_board.make_move_click(received_event.pos[0], received_event.pos[1])

        elif received_event.type == pygame.USEREVENT:

            if received_event.action == 'MAKE-MOVE':
                outbound_message_queue.put('%s|MOVE|%d|%d' % (our_team, received_event.row, received_event.col))

            elif received_event.action == 'MOVE':
                if received_event.team == their_team:
                    our_board.check_move(received_event.row, received_event.col)

            elif received_event.action == 'WE-GOT-HIT':
                outbound_message_queue.put('%s|HIT|%d|%d' % (our_team, received_event.row, received_event.col))

            elif received_event.action == 'WE-WERE-MISSED':
                outbound_message_queue.put('%s|MISS|%d|%d' % (our_team, received_event.row, received_event.col))

            elif received_event.action == 'MISS' and received_event.team == their_team:
                their_board.record_miss(received_event.row, received_event.col)

            elif received_event.action == 'HIT' and received_event.team == their_team:
                their_board.record_hit(received_event.row, received_event.col)

            elif received_event.action == 'FIND_ME':
                if not received_event.team == our_team:
                    teams.found_team(received_event.team, received_event.row)

            elif received_event.action == 'STATUS':
                status_bar.update_text(received_event.text)

            elif received_event.action == 'SELECT_TEAM':
                selected_their_team = received_event.team
                selected_their_team_first_move = received_event.first_move_number
                start_game_button.set_enabled(can_start_game())


    screen.fill(DARK_BLUE)
    our_board.draw(screen)
    status_bar.draw(screen)

    if game_state == STATE_PREPARING:
        save_positions_button.draw(screen)
        load_positions_button.draw(screen)
        start_game_button.draw(screen)
        teams.draw(screen)
    else:
        their_board.draw(screen)

    clock.tick(5)
    pygame.display.update()


network.shutdown()
sending_thread.join()
receiving_thread.join()

pygame.quit()
sys.exit(0)
