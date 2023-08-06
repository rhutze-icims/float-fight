import argparse
from config import *
from game import Game
from network import Network
import pygame
from random import randint
import signal
import sys


parser = argparse.ArgumentParser(description="Float Fight, made with pygame")
parser.add_argument('--number', required=True, help="A game number from 0-1000")
args = parser.parse_args()

game_number = int(args.number)
our_team_id = randint(0, 1000)

if game_number < 0 or game_number > 1000:
    print("\nERROR: The game number must be between 0 and 1000.\n")
    sys.exit(1)

pygame.init()
pygame.display.set_caption(f"Float Fight - Game #{game_number}")
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()


def handle_sigint(sig, frame):
    global shutdown_signal
    if sig == signal.SIGINT:
        print('Received Ctrl+C. Shutting down...')
        if shutdown_signal is True:
            # Just in case the first attempt to CTRL+C didn't work.
            sys.exit(0)
        shutdown_signal = True


shutdown_signal = False
signal.signal(signal.SIGINT, handle_sigint)

network = Network(game_number, our_team_id)
networking_thread = network.start()

game = Game(screen, network.get_messages_to_send(), our_team_id)
game.draw_game()
pygame.display.update()

while not shutdown_signal:
    clock.tick(10) # limits frames per second to 10

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            shutdown_signal = True
        elif event.type == pygame.USEREVENT and event.action == ACTION_GAME_STATE_CHANGED:
            network.update_game_state(event.state)
            game.draw_game()
            pygame.display.update()

        try:
            if game.handle_event(event) is True:
                game.draw_game()
                pygame.display.update()
        except Exception as ex:
            print(f"ERROR:    {ex}")

network.shutdown()
networking_thread.join()

pygame.quit()
sys.exit(0)
