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


def handle_sigint(sig, frame) -> None:
    """
    If the user presses CTRL+C or closes the game window, this function will get called. It sets a variable
    called shutdown_signal to be True. The game's event loop keeps going and going. That is, unless it sees
    this variable change, in which case the program will exit.
    """
    global shutdown_signal
    if sig == signal.SIGINT:
        print('Received Ctrl+C. Shutting down...')
        shutdown_signal = True


shutdown_signal = False
# handle_sigint is the function that is defined a few lines up. We're telling Python that, if the window gets
# closed, handle_sigint is the function that should get called so that we can do something in response.
signal.signal(signal.SIGINT, handle_sigint)

network = Network(game_number, our_team_id)
networking_thread = network.start()

game = Game(screen, network.get_messages_to_send(), our_team_id)
pygame.display.update()

# This is the game's event loop, which keeps going and going, handling any events
# that pygame tells it about.
while not shutdown_signal:
    clock.tick(10) # limits frames per second to 10

    for event in pygame.event.get():
        # All events come through here. All events have a type, and if the type is USEREVENT, we know that
        # it's one that our own code created, to announce to the rest of the code that something has happened.
        # For example, maybe a message arrived from our opponent, or maybe one of the cells on the board needs
        # to announce that it was clicked and a move was made.

        try:
            if event.type == pygame.QUIT:
                shutdown_signal = True
            elif event.type == pygame.USEREVENT and event.action == ACTION_GAME_STATE_CHANGED:
                # While the game is in a preparing state, the network code knows to keep announcing "I'm here!
                # I'm here!" so our opponent can find us. Once the game state changes, the network code knows
                # not to do that anymore. That's why we tell it about game state changes, too.
                network.update_game_state(event.state)

            # Redrawing the whole screen too often can be a lot of work for pygame, so we only do it when we need
            # to. The game module's handle_event does all sorts of things. It was written to always return either
            # True or False when it's done. True means that something changed that should make the screen look
            # different and we should redraw it. False means that everything can keep looking the same.
            if game.handle_event(event) is True:
                game.draw_game()
                pygame.display.update()

        except Exception as ex:
            print(f"ERROR:    {ex}")

network.shutdown()
networking_thread.join()

pygame.quit()
sys.exit(0)
