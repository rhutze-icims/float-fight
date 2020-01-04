import pygame
import queue
import sys

from board import Board, OURS, THEIRS
from button import Button
from config import DARK_BLUE, GAME_SIZE, SCREEN_HEIGHT, SCREEN_WIDTH
from network import Network
from status_bar import StatusBar

shutdown_signal = False

if len(sys.argv) < 2 or len(sys.argv[1]) > 20:
    print("\nProvide your team name of up to 20 characters when starting the application.\nExample: python main.py \"My Team Name\"\n")
    sys.exit(1)
our_team = sys.argv[1]

if our_team == "A":
    their_team = "B"
else:
    their_team = "A"

pygame.init()
pygame.display.set_caption('Float Fight - %s' % our_team)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
screen.fill(DARK_BLUE)

clock = pygame.time.Clock()
images = {
    'ocean': pygame.image.load('ocean.jpg').convert(),
    'explosion': pygame.image.load('explosion.jpg').convert(),
    'ship': pygame.image.load('battleship.jpg').convert()
}

outbound_message_queue = queue.Queue()

our_board = Board(GAME_SIZE, 5, 0, OURS, images)
their_board = Board(GAME_SIZE, 580, 0, THEIRS, images)
load_positions_button = Button("Load", 110, 770, our_board.load_positions_from_file)
save_positions_button = Button("Save", 170, 770, our_board.save_positions_to_file)
status_bar = StatusBar()
status_bar.update_text('Choose your positions and an opponent...')

network = Network(outbound_message_queue)
receiving_thread = network.start_receiving()
sending_thread = network.start_sending()

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
            else:
                our_board.toggle_ship_click(received_event.pos[0], received_event.pos[1])
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

            elif received_event.action == 'STATUS':
                status_bar.update_text(received_event.text)

    our_board.draw(screen)
    their_board.draw(screen)
    save_positions_button.draw(screen)
    load_positions_button.draw(screen)
    status_bar.draw(screen)

    pygame.display.update()
    clock.tick(15)

network.shutdown()
sending_thread.join()
receiving_thread.join()

pygame.quit()
sys.exit(0)
