import argparse
from config import *
from game import Game
from network import Network
import pygame
from random import randint
import signal
import sys


parser = argparse.ArgumentParser(description="Float Fight, made with pygame")
parser.add_argument('--team', required=True, help="Your team name (i.e. \"Team A\")")
args = parser.parse_args()

our_team = args.team
our_team_first_move = randint(0, 1000)

pygame.init()
pygame.display.set_caption(f"Float Fight - {our_team}")
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()


def handle_sigint(sig, frame):
    global shutdown_signal
    if sig == signal.SIGINT:
        print('Received Ctrl+C. Shutting down...')
        shutdown_signal = True


shutdown_signal = False
signal.signal(signal.SIGINT, handle_sigint)

network = Network(our_team, our_team_first_move)
networking_thread = network.start()

game = Game(screen, network.get_messages_to_send(), our_team, our_team_first_move)
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

        if game.handle_event(event) is True:
            game.draw_game()
            pygame.display.update()

network.shutdown()
networking_thread.join()

pygame.quit()
sys.exit(0)
