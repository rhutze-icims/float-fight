# GWC Float Fight

This is a partially developed game that can be used for teaching purposes. It is for two players 
that are on the same local network. Each player positions their ships along a grid. Each player 
keeps their positions secret from the other. Then, they take turns guessing the coordinates of 
the other player's ships. The winner is the first player to discover all of their opponent's
positions.

Each instance of the game that is running must have a separate team name assigned to it at startup.

The instances use multicast networking to communicate with each other. These are packets that 
everyone on a local network receives. It is even possible to run two copies of the
game on the same machine, perhaps on different monitors, and they will find each other.
The instances know to only respond to messages that mention either their own team name or that 
of their opponent.

# Preparing

`python3 -m pip install -r requirements.txt`

# Testing

`python3 -m pytest`

# Running

`python3 main.py --team "My Team Name"`

If you are experimenting locally, run a second instance with a different team name.

# TODO:

* Check whether all positions have been found.
* Check for valid ship placement before game starts.
* When lots of teams are seeking opponents at once, extend their buttons into a second column.
* Allow use of keyboard arrows for grid navigation and space/click confirmation.
