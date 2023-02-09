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
#  [ ] Start : Starts the game.
#  [ ] Update : Updates the game
#  [ ] End : Ends the game.
#  [ ] Quit : Quits the game.
#  [ ] Restart : Restarts the game.
#  [ ] Pause : Pauses the game.
#  [ ] Unpause : Unpauses the game.
#  [x] Save : Saves the game to a file.
#  [x] Load : Loads the game from a file.
#  [ ] Set Settings : Sets the settings for the game.
#  [ ] Set Users : Sets the users for the game. (Single player mode only)
#  [ ] Get Questions : Gets the questions from the server (API).
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

from Maxs_Modules.files import SaveFile, load_questions_from_file
from Maxs_Modules.tools import debug, error, try_convert, set_if_none, get_user_input_of_type, strBool
from Maxs_Modules.renderer import Menu


# - - - - - - - Variables - - - - - - -#
data_folder = "UserData/Games/"

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

        # If there is more than 1000 save files, then something probably went wrong
        if name_index > 1000:
            raise Exception("Could not find a save file name")

    return save_name


def get_saved_games():
    # Get a list of all the files in the data folder
    files = os.listdir(data_folder)
    debug("Files in data folder: " + str(files), "Game")

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

    def load(self, data):
        self.name = data.get("name")
        self.colour = data.get("colour")
        self.icon = data.get("icon")
        self.points = data.get("points")
        self.correct = data.get("correct")
        self.wrong = data.get("wrong")
        self.questions_missed = data.get("questions_missed")


class Question:
    category = None
    q_type = None       # Has to be q_type because type is a python keyword
    difficulty = None
    question = None
    correct_answer = None
    incorrect_answers = None

    def __init__(self, category, q_type, difficulty, question, correct_answer, incorrect_answers):
        self.category = category
        self.q_type = q_type
        self.difficulty = difficulty
        self.question = question
        self.correct_answer = correct_answer
        self.incorrect_answers = incorrect_answers

    def load(self, data):
        self.category = data.get("category")
        self.q_type = data.get("q_type")
        self.difficulty = data.get("difficulty")
        self.question = data.get("question")
        self.correct_answer = data.get("correct_answer")
        self.incorrect_answers = data.get("incorrect_answers")


class Game(SaveFile):

    # User Chosen Settings
    host_a_server = None
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
    online_enabled = None

    # Game data
    users = None
    questions = None

    def __init__(self, online_enabled, quiz_save=None):
        # Call the super class and pass the save file name, this will automatically load the settings

        # If the quiz save is not none, then load the quiz save because the user wants to continue a game otherwise
        # generate a new save file
        if quiz_save is not None:
            super().__init__(data_folder + quiz_save)
        else:
            super().__init__(data_folder + generate_new_save_file())

        # Set the online enabled variable, note it is not saved because the online state can change between runs
        self.online_enabled = online_enabled

        # Load User Settings
        self.host_a_server = try_convert(self.save_data.get("host_a_server"), str)
        self.time_limit = try_convert(self.save_data.get("time_limit"), int)
        self.show_score_after_question_or_game = try_convert(self.save_data.get("show_score_after_question_or_game"), str)
        self.show_correct_answer_after_question_or_game = try_convert(self.save_data.get("show_correct_answer_after_question_or_game"), str)
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

        # Set the default settings if the settings are none
        self.set_settings_default()

        # Convert the data
        self.convert_users()
        self.convert_questions()

    def set_settings_default(self):
        # User Chosen Settings
        self.host_a_server = set_if_none(self.host_a_server, False)
        self.time_limit = set_if_none(self.time_limit, 10)
        self.show_score_after_question_or_game = set_if_none(self.show_score_after_question_or_game, "Question")
        self.show_correct_answer_after_question_or_game = set_if_none(self.show_correct_answer_after_question_or_game, "Question")
        self.points_for_correct_answer = set_if_none(self.points_for_correct_answer, 1)
        self.points_for_incorrect_answer = set_if_none(self.points_for_incorrect_answer, -1)
        self.points_for_no_answer = set_if_none(self.points_for_no_answer, 0)
        self.points_multiplier_for_a_streak = set_if_none(self.points_multiplier_for_a_streak, 1.1)
        self.compounding_amount_for_a_streak = set_if_none(self.compounding_amount_for_a_streak, 1)
        self.pick_random_question = set_if_none(self.pick_random_question, True)
        self.bot_difficulty = set_if_none(self.bot_difficulty, 50)
        self.server_name = set_if_none(self.server_name, "Quiz Game Server")
        self.server_port = set_if_none(self.server_port, 1234)
        self.max_players = set_if_none(self.max_players, 4)
        self.how_many_players = set_if_none(self.how_many_players, 1)
        self.how_many_bots = set_if_none(self.how_many_bots, 0)
        self.quiz_category = set_if_none(self.quiz_category, "Any")
        self.quiz_difficulty = set_if_none(self.quiz_difficulty, "Any")
        self.question_amount = set_if_none(self.question_amount, 10)
        self.question_type = set_if_none(self.question_type, "Any")

        # State Settings
        self.current_question = set_if_none(self.current_question, 0)
        self.current_user_playing = set_if_none(self.current_user_playing, 0)

        # Game Data
        self.users = set_if_none(self.users, [])
        self.questions = set_if_none(self.questions, [])

    def set_settings(self):
        game_settings_how_to(self)

    def convert_users(self):

        # Check if the users list is empty
        if len(self.users) == 0:
            return

        # Check if the user is already a User object
        if type(self.users[0]) is User:
            return

        # For each user in the list of users convert the dict to a User object using the load() function
        for x in range(len(self.users)):
            user_object = User()
            user_object.load(self.users[x])
            self.users[x] = user_object

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

    def get_questions(self):

        # Check if the user is online
        if self.online_enabled:

            # Import the api_get_questions function, this is only imported if the user is online as it is not needed
            # if the user is offline and dont want to run the requests installation
            from Maxs_Modules.network import api_get_questions

            # Use the api to get the questions
            self.questions = api_get_questions(self.question_amount, self.quiz_category, self.quiz_difficulty, self.question_type)

        else:

            # Load the question from the saved questions
            self.questions = load_questions_from_file()

        # Convert the data into a list of Question objects
        self.convert_questions()

    def convert_questions(self):

        # Check if there are any questions
        if len(self.questions) == 0:
            return

        # Check if the questions are already in the correct format
        if type(self.questions[0]) is Question:
            return

        # For each question in the list of questions convert the dict to a Question object using the load() function
        for x in range(len(self.questions)):
            question_object = Question()
            question_object.load(self.questions[x])
            self.questions[x] = question_object

    def begin(self):
        for user in self.users:
            print(user.name)

    def save(self):
        # Create the save data for the UserSettings object
        self.save_data = self.__dict__

        # Convert the user class to a dict
        for user_index in range(len(self.users)):
            self.save_data["users"][user_index] = self.users[user_index].__dict__

        # Call the super class save function
        super().save()

        # Convert the data back to the original format
        self.convert_users()

# - - - - - - - MENUS - - - - - - -#


def game_settings_local(game):
    local_menu_options = ["How many players", "Next"]
    local_menu_values = [str(game.how_many_players), "Gameplay"]
    single_player_menu = Menu("Game Settings: Single Player", [local_menu_options, local_menu_values], True)
    single_player_menu.show()

    match single_player_menu.user_input:
        case "How many players":
            game.how_many_players = get_user_input_of_type(int, "How many players")

        case "Next":
            game.set_users()


def game_settings_networking(game):
    networking_menu_options = ["Server Name", "Server Port", "Max Players", "Next"]
    networking_menu_values = [str(game.server_name), str(game.server_port), str(game.max_players), "Players"]

    networking_menu = Menu("Game Settings: Networking", [networking_menu_options, networking_menu_values], True)
    networking_menu.show()

    match networking_menu.user_input:

        case "Server Name":
            game.server_name = get_user_input_of_type(str, "Server Name")

        case "Server Port":
            game.server_port = get_user_input_of_type(int, "Server Port")

        case "Max Players":
            game.max_players = get_user_input_of_type(int, "Max Players")

        case "Next":
            print("NETWORKING UNDEFINED")
            while True:
                pass


def game_settings_gameplay(game):
    game_play_menu_options = ["Host a server", "Time limit", "Show score after Question/Game",
                                                     "Show correct answer after Question/Game",
                                                     "Points for correct answer", "Points for incorrect answer",
                                                     "Points for no answer", "Points multiplier for a streak",
                                                     "Compounding amount for a streak", "Pick random question",
                                                     "Bot difficulty", "Number of bots", "Next"]

    game_play_menu_values = [str(game.host_a_server), str(game.time_limit), str(game.show_score_after_question_or_game),
                             str(game.show_correct_answer_after_question_or_game),
                             str(game.points_for_correct_answer), str(game.points_for_incorrect_answer),
                             str(game.points_for_no_answer),
                             str(game.points_multiplier_for_a_streak), str(game.compounding_amount_for_a_streak),
                             str(game.pick_random_question),
                             str(game.bot_difficulty), str(game.how_many_bots)]


    if game.host_a_server:
        game_play_menu_values.append("Networking Settings")
    elif not game.host_a_server:
        game_play_menu_values.append("Local Settings")

    gameplay_menu = Menu("Game Settings: Gameplay", [game_play_menu_options, game_play_menu_values], True)
    gameplay_menu.show()

    match gameplay_menu.user_input:
        case "Host a server":
            game.host_a_server = get_user_input_of_type(strBool, "Host a server (True/False)")

        case "Time limit":
            game.time_limit = get_user_input_of_type(int, "Time limit (seconds)")

        case "Show score after Question/Game":
            game.show_score_after_question_or_game = get_user_input_of_type(str, "Show score after: (Question/Game)", ["Question", "Game"])

        case "Show correct answer after Question/Game":
            game.show_correct_answer_after_question_or_game = get_user_input_of_type(str, "Show correct answer after: (Question/Game)", ["Question", "Game"])

        case "Points for correct answer":
            game.points_for_correct_answer = get_user_input_of_type(int, "Points for correct answer")

        case "Points for incorrect answer":
            game.points_for_incorrect_answer = get_user_input_of_type(int, "Points for incorrect answer")

        case "Points for no answer":
            game.points_for_no_answer = get_user_input_of_type(int, "Points for no answer")

        case "Points multiplier for a streak":
            game.points_multiplier_for_a_streak = get_user_input_of_type(int, "Points multiplier for a streak")

        case "Compounding amount for a streak":
            game.compounding_amount_for_a_streak = get_user_input_of_type(int, "Compounding amount for a streak")

        case "Pick random question":
            game.pick_random_question = get_user_input_of_type(strBool, "Pick random question (True/False)")

        case "Bot difficulty":
            game.bot_difficulty = get_user_input_of_type(int , "Bot difficulty (1-10)", range(1, 11))

        case "Number of bots":
            game.how_many_bots = get_user_input_of_type(int, "Number of bots")

        case "Next":
            if game.host_a_server:
                game_settings_networking(game)
            elif not game.host_a_server:
                game_settings_local(game)

            # Skip the function loop
            return

    game_settings_gameplay(game)


def game_settings_how_to(game):
    os.system("cls")

    print("Game Settings: How To")
    time.sleep(1)

    print("You will be shown menus relating to the game settings, you can change the settings by typing in the number "
          "of the option you want to change, otherwise the default will be used")

    input("Press enter to continue...")
    game_settings_gameplay(game)
