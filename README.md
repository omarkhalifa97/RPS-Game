# Description
A simple Rock-Paper-Scissors game server socket in Python with waiting list players. 

# Features
Accept connections: The server should accept connections from clients and add them to a waiting list.

Waiting list: The server should maintain a waiting list of players who are waiting for a match. When a new player connects, the server should add them to the waiting list. If there are not enough players to start a game, the server should keep them in the waiting list.

Matchmaking: Once two clients have connected, the server should match them and initiate the game. If there are not enough players, the server should keep them in the waiting list.

Play game: The server should handle the logic for determining the winner of the game and broadcast the result to all clients.

Multiplayer support: The server should be able to handle multiple games simultaneously, with each game being played by two clients.

# How to run
(this works for windows xp/7/8/10/11
@ Enter following commands in CMD or Powershell

_ pyhton ./Server.py    # to start server

_ python ./Clinet.py	# to start the game


