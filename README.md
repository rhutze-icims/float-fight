# Girls Who Code Float Fight

This is a partially developed game that can be used for teaching purposes. It is for two players 
that are on the same local network. Each player positions their ships along a grid. Each player 
keeps their positions secret from the other. Then, they take turns guessing the coordinates of 
the other player's ships. The winner is the first player to discover all of their opponent's
positions.

You and your opponent must agree on a game number between 0 and 1000. When starting up the game,
you will both provide this same number so that your instances can find each other.

The instances use multicast networking to communicate with each other. These are packets that 
everyone on a local network receives. It is even possible to run two copies of the
game on the same machine, and they will find each other.
The instances know to only respond to messages that mention either their own team name or that 
of their opponent.

# Preparing

`python3 -m pip install --upgrade pip`
`python3 -m pip install -r requirements.txt`

# Testing

`python3 -m pytest`

# Running

`python3 main.py --number 401`

If you are experimenting locally, run a second instance with the same game number.

# TODO:

* Check whether all positions have been found.
* Check for valid ship placement before game starts.
* Allow use of keyboard arrows for grid navigation and space/click confirmation.
