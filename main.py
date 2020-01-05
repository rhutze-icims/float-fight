from config import *
from game import Game
from network import Network
import pygame
from random import randint
import signal
import sys


def handle_sigint(sig, frame):
    global shutdown_signal
    if sig == signal.SIGINT:
        print('Received Ctrl+C. Shutting down...')
        shutdown_signal = True


if len(sys.argv) < 2 or len(sys.argv[1]) > 20:
    print("\nProvide your team name of up to 20 characters when starting the application." +
          "\nExample: python main.py \"My Team Name\"\n")
    sys.exit(1)
our_team = sys.argv[1]
our_team_first_move = randint(0, 1000)

pygame.init()
pygame.display.set_caption('Float Fight - %s' % our_team)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

shutdown_signal = False
signal.signal(signal.SIGINT, handle_sigint)

network = Network(our_team, our_team_first_move)
receiving_thread = network.start_receiving()
sending_thread = network.start_sending()

game = Game(screen, network.get_messages_to_send(), our_team, our_team_first_move)

while not shutdown_signal:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            shutdown_signal = True
        elif event.type == pygame.USEREVENT and event.action == ACTION_GAME_STATE_CHANGED:
            network.update_game_state(event.state)
        game.handle_event(event)

    clock.tick(5)
    pygame.display.update()

network.shutdown()
sending_thread.join()
receiving_thread.join()

pygame.quit()
sys.exit(0)
