# Spec: (JUMP TO LINE 60 TO SKIP)
#  - This module contains the Game class, which is the main class for the game.
#  - When playing in single player mode person A goes through the whole quiz then person B goes through the whole quiz.
#  - When playing in multiplayer mode person A and B go through the quiz simultaneously.
# External Functions:
#  - Join Game : Connects to a server and joins a game.
#  - Play Game : Starts a game.
#  - Init : Initializes the GameManager class.
#
# Internal Functions:
#  == (Main Gameplay functions) ==
#  - Init : Initializes the GameManager class.
#  - Main : The main function for the game.
#  - Start : Starts the game.
#  - Update : Updates the game
#  - End : Ends the game.
#  - Quit : Quits the game.
#  - Restart : Restarts the game.
#  - Pause : Pauses the game.
#  - Unpause : Unpauses the game.
#  - Save : Saves the game to a file.
#  - Load : Loads the game from a file.
#  == (Networking functions) ==
#  - Connect : Connects to a server.
#  - Disconnect : Disconnects from a server.
#  - Send : Sends data to a server.
#  - Receive : Receives data from a server.
#  - Sync : Syncs the game with the server.
#  - Host : Hosts a server.
#  - Get Quiz Data : Gets the quiz data from the server (API).
#  == (Gameplay functions) ==
#  - Display Options : Displays the options for the question.
#  - Mark Answer : Marks the answer as correct or incorrect.
#  - Get Input : Gets the user input.
#  - Display Score : Displays the score of each player.
#  - Bot Answer : Makes the bot answer the question.
#
# Settings:
#  == (Gameplay Settings) ==
#  - Time Limit : The time limit for each question.
#  - Show Score after Question or Game : Whether to show the score after each question or after the game (This means that if it is shown after each question in single player, a snapshot of each players score at that question is needed).
#  - Show Correct Answer after Question or Game : Whether to show the correct answer after each question or after the game.
#  - Points for Correct Answer : The points for a correct answer.
#  - Points for Incorrect Answer : The points for an incorrect answer.
#  - Points for No Answer : The points for no answer.
#  - Points multiplier for a streak : The points multiplier for a streak.
#  - Compounding amount for a streak : The compounding amount for a streak.
#  - Pick Random Question : Whether to pick a random question or not once the time limit has been reached.
#  - Bot Difficulty : The difficulty of the bot (% chance of picking the right awnser out of 100).
#  == (Network Settings) ==
#  - Server Name : The name of the server.
#  - Server Port : The port of the server (1234 by default).
#  - Max Players : The maximum amount of players.
#  == (Single Player Settings) ==
#  - How many players : The amount of players.
#  - How many bots : The amount of bots.
#  == (Quiz Settings) ==
#  - Quiz Category : The category of the quiz.
#  - Quiz Difficulty : The difficulty of the quiz.
#  - Question Amount : The amount of questions.
#  - Question Type : The type of questions (True/False, Multi choice).
#  == (Player Settings) ==
#  - Player Name : The name of the player.
#  - Player Colour : The colour of the player.
#  - Player Icon : The icon of the player (GUI Only).


# - - - - - - - Imports - - - - - - -#


# - - - - - - - Variables - - - - - - -#
# - - - - - - - Functions - - - - - - -#
# - - - - - - - Classes - - - - - - -#


# - - - - - - - MENUS - - - - - - -#