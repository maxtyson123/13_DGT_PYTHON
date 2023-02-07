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
#  [ ] Init : Initializes the GameManager class.
#  [ ] Main : The main function for the game.
#  [ ] Start : Starts the game.
#  [ ] Update : Updates the game
#  [ ] End : Ends the game.
#  [ ] Quit : Quits the game.
#  [ ] Restart : Restarts the game.
#  [ ] Pause : Pauses the game.
#  [ ] Unpause : Unpauses the game.
#  [x] Save : Saves the game to a file.
#  [ ] Load : Loads the game from a file.
#  == (Networking functions) ==
#  [ ] Connect : Connects to a server.
#  [ ] Disconnect : Disconnects from a server.
#  [ ] Send : Sends data to a server.
#  [ ] Receive : Receives data from a server.
#  [ ] Sync : Syncs the game with the server.
#  [ ] Host : Hosts a server.
#  [ ] Get Quiz Data : Gets the quiz data from the server (API).
#  == (Gameplay functions) ==
#  [ ] Display Options : Displays the options for the question.
#  [ ] Mark Answer : Marks the answer as correct or incorrect.
#  [ ] Get Input : Gets the user input.
#  [ ] Display Score : Displays the score of each player.
#  [ ] Bot Answer : Makes the bot answer the question.
#
# Settings:
#  == (Gameplay Settings) ==
#  [ ] Game Mode : The game mode (Local Players or Multiplayer).
#  [ ] Time Limit : The time limit for each question.
#  [ ] Show Score after Question or Game : Whether to show the score after each question or after the game (This means that if it is shown after each question in single player, a snapshot of each players score at that question is needed).
#  [ ] Show Correct Answer after Question or Game : Whether to show the correct answer after each question or after the game.
#  [ ] Points for Correct Answer : The points for a correct answer.
#  [ ] Points for Incorrect Answer : The points for an incorrect answer.
#  [ ] Points for No Answer : The points for no answer.
#  [ ] Points multiplier for a streak : The points multiplier for a streak.
#  [ ] Compounding amount for a streak : The compounding amount for a streak.
#  [ ] Pick Random Question : Whether to pick a random question or not once the time limit has been reached.
#  [ ] Bot Difficulty : The difficulty of the bot (% chance of picking the right awnser out of 100).
#  == (Network Settings) ==
#  [ ] Server Name : The name of the server.
#  [ ] Server Port : The port of the server (1234 by default).
#  [ ] Max Players : The maximum amount of players.
#  == (Single Player Settings) ==
#  [ ] How many players : The amount of players.
#  [ ] How many bots : The amount of bots.
#  == (Quiz Settings) ==
#  [ ] Quiz Category : The category of the quiz.
#  [ ] Quiz Difficulty : The difficulty of the quiz.
#  [ ] Question Amount : The amount of questions.
#  [ ] Question Type : The type of questions (True/False, Multi choice).
#  == (Player Settings) ==
#  [ ] Player Name : The name of the player.
#  [ ] Player Colour : The colour of the player.
#  [ ] Player Icon : The icon of the player (GUI Only).


# - - - - - - - Imports - - - - - - -#
import os
import time

from Maxs_Modules.files import SaveFile
from Maxs_Modules.tools import debug, error, try_convert
from Maxs_Modules.renderer import Menu

# - - - - - - - Variables - - - - - - -#
data_folder = "UserData/Games"

# - - - - - - - Functions - - - - - - -#


def generate_new_save_file():
    # Get all the save files
    already_saved = get_saved_games()

    # Create a name for the save file
    name = "Game_"
    name_index = 0
    save_name = name + str(name_index) + ".json"

    # Check if the save file already exists
    while save_name in already_saved:
        name_index += 1
        save_name = name + str(name_index) + ".json"

        # If there is more then 1000 save files, then something probably went wrong
        if name_index > 1000:
            raise Exception("Could not find a save file name")

    return save_name


def get_saved_games():
    # Get a list of all the files in the data folder
    files = os.listdir(data_folder)

    # Remove all the files that are not .json files
    for file in files:
        if not file.endswith(".json"):
            files.remove(file)

    return files


# - - - - - - - Classes - - - - - - -#

class User:
    name = None
    colour = None
    icon = None
    points = 0
    correct = 0
    wrong = 0
    questions_missed = 0

    def __int__(self, name, colour, icon):
        self.name = name
        self.colour = colour
        self.icon = icon


class Game(SaveFile):

    # User Chosen Settings
    game_mode = None
    time_limit = None
    show_score_after_question_or_game = None
    show_correct_answer_after_question_or_game = None
    points_for_correct_answer = None
    points_for_incorrect_answer = None
    points_for_no_answer = None
    points_multiplier_for_a_streak = None
    compounding_amount_for_a_streak = None
    pick_random_question = None
    bot_difficulty = None
    server_name = None
    server_port = None
    max_players = None
    how_many_players = None
    how_many_bots = None
    quiz_category = None
    quiz_difficulty = None
    question_amount = None
    question_type = None

    # State Settings
    current_question = None
    current_user_playing = None

    # Game data
    users = None
    questions = None

    def __init__(self, quiz_save=None):
        # Call the super class and pass the save file name, this will automatically load the settings

        # If the quiz save is not none, then load the quiz save because the user wants to continue a game otherwise
        # generate a new save file
        if quiz_save is not None:
            super().__init__(data_folder + quiz_save)
        else:
            super().__init__(data_folder + generate_new_save_file())

        # Load User Settings
        self.game_mode = try_convert(self.save_data.get("game_mode"), str)
        self.time_limit = try_convert(self.save_data.get("time_limit"), int)
        self.show_score_after_question_or_game = try_convert(self.save_data.get("show_score_after_question_or_game"), bool)
        self.show_correct_answer_after_question_or_game = try_convert(self.save_data.get("show_correct_answer_after_question_or_game"), bool)
        self.points_for_correct_answer = try_convert(self.save_data.get("points_for_correct_answer"), int)
        self.points_for_incorrect_answer = try_convert(self.save_data.get("points_for_incorrect_answer"), int)
        self.points_for_no_answer = try_convert(self.save_data.get("points_for_no_answer"), int)
        self.points_multiplier_for_a_streak = try_convert(self.save_data.get("points_multiplier_for_a_streak"), int)
        self.compounding_amount_for_a_streak = try_convert(self.save_data.get("compounding_amount_for_a_streak"), int)
        self.pick_random_question = try_convert(self.save_data.get("pick_random_question"), bool)
        self.bot_difficulty = try_convert(self.save_data.get("bot_difficulty"), int)
        self.server_name = try_convert(self.save_data.get("server_name"), str)
        self.server_port = try_convert(self.save_data.get("server_port"), int)
        self.max_players = try_convert(self.save_data.get("max_players"), int)
        self.how_many_players = try_convert(self.save_data.get("how_many_players"), int)
        self.how_many_bots = try_convert(self.save_data.get("how_many_bots"), int)
        self.quiz_category = try_convert(self.save_data.get("quiz_category"), str)
        self.quiz_difficulty = try_convert(self.save_data.get("quiz_difficulty"), str)
        self.question_amount = try_convert(self.save_data.get("question_amount"), int)
        self.question_type = try_convert(self.save_data.get("question_type"), str)

        # Load State Settings
        self.current_question = try_convert(self.save_data.get("current_question"), int)
        self.current_user_playing = try_convert(self.save_data.get("current_user_playing"), int)

        # Load Game Data
        self.users = try_convert(self.save_data.get("users"), list)
        self.questions = try_convert(self.save_data.get("questions"), list)

    def set_settings(self):
        game_settings_how_to(self)

    def set_users(self):
        userId = 0
        while userId != self.how_many_players:

            # Clear the screen
            os.system("cls")

            # Create a new user
            userId += 1
            user = User()

            # Get name and check if it is valid
            while user.name is None:
                user.name = try_convert(input("Enter the name for user " + str(userId) + ": "), str)

            # Get colour
            colour_menu = Menu("Choose a colour for " + user.name, ["Red", "Green", "Blue", "Yellow", "Purple", "Orange", "Pink", "Black", "White"])
            colour_menu.show()
            user.colour = colour_menu.user_input

            # Add to list of users
            self.users.append(user)

    def begin(self):
        pass

    def save(self):
        # Create the save data for the UserSettings object
        self.save_data = self.__dict__

        # Call the super class save function
        super().save()

# - - - - - - - MENUS - - - - - - -#


def game_settings_single_player(game):
    single_player_menu = Menu("Game Settings: Single Player", ["How many players", "Next"])
    single_player_menu.show()

    match single_player_menu.user_input:
        case "Next":
            game.set_users()


def game_settings_networking(game):
    networking_menu = Menu("Game Settings: Networking", ["Server Name", "Server Port", "Max Players", "Next"])
    networking_menu.show()

    match networking_menu.user_input:
        case "Next":
            print("NETWORKING UNDEFINED")
            while True:
                pass


def game_settings_gameplay(game):
    gameplay_menu = Menu("Game Settings: Gameplay", ["Game Mode", "Time limit", "Show score after Question/Game",
                                                     "Show correct answer after Question/Game",
                                                     "Points for correct answer", "Points for incorrect answer",
                                                     "Points for no answer", "Points multiplier for a streak",
                                                     "Compounding amount for a streak", "Pick random question",
                                                     "Bot difficulty", "Number of bots", "Next"])
    gameplay_menu.show()

    match gameplay_menu.user_input:
        case "Next":
            if game.game_mode == "Single Player":
                game_settings_single_player(game)
            elif game.game_mode == "Multiplayer":
                game_settings_networking(game)


def game_settings_how_to(game):
    os.system("cls")

    print("Game Settings: How To")
    time.sleep(1)

    print("You will be shown menus relating to the game settings, you can change the settings by typing in the number "
          "of the option you want to change, otherwise the default will be used")

    input("Press enter to continue...")
    game_settings_gameplay(game)
