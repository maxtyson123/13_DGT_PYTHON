# Spec: (JUMP TO LINE 60 TO SKIP)
#  - This module contains the Game class, which is the main class for the game.
#  - When playing in single player mode person A goes through the whole quiz then person B goes through the whole quiz.
#  - When playing in multiplayer mode person A and B go through the quiz simultaneously.
#  - Terminology: User = Person playing the game, Player = User or Bot.
# External Functions:
#  - Join Game : Connects to a server and joins a game.
#  - Play Game : Starts a game.
#
# Internal Functions:
#  == (Main Gameplay functions) ==
#  [x] Start : Starts the game.
#  [x] Quit : Quits the game.
#  [x] Restart : Restarts the game.
#  [x] Save : Saves the game to a file.
#  [x] Load : Loads the game from a file.
#  [x] Set Settings : Sets the settings for the game.
#  [x] Set Users : Sets the users for the game. (Single player mode only)
#  [x] Get Questions : Gets the questions from the server (API).
#  == (Networking functions) ==
#  [x] Connect : Connects to a server.
#  [x] Disconnect : Disconnects from a server.
#  [x] Send : Sends data to a server.
#  [x] Receive : Receives data from a server.
#  [ ] Sync : Syncs the game with the server.
#  [x] Host : Hosts a server.
#  [x] Get Quiz Data : Gets the quiz data from the server (API).
#  == (Gameplay functions) ==
#  [x] Display Options : Displays the options for the question.
#  [x] Mark Answer : Marks the answer as correct or incorrect.
#  [x] Get Input : Gets the user input.
#  [x] Display Score : Displays the score of each player.
#  [x] Play Again Or Quit : Asks the user if they want to play again or quit.
#  [x] Bot Answer : Makes the bot answer the question.
#
# Settings:
#  == (Gameplay Settings) ==
#  [x] Game Mode : The game mode (Local Players or Multiplayer).
#  [x] Time Limit : The time limit for each question.
#  [x] Show Score after Question or Game : Whether to show the score after each question or after the game
#  [x] Show Correct Answer after Question or Game : Whether to show the correct answer after each question or after the
#      game.
#  [x] Points for Correct Answer : The points for a correct answer.
#  [x] Points for Incorrect Answer : The points for an incorrect answer.
#  [x] Points for No Answer : The points for no answer.
#  [x] Points multiplier for a streak : The points multiplier for a streak.
#  [x] Compounding amount for a streak : The compounding amount for a streak.
#  [x] Randomise Questions : Whether to randomise the questions or not.
#  [x] Randomise Answers : Whether to randomise the answers placement or not.
#  [x] Pick Random Question : Whether to pick a random question or not once the time limit has been reached.
#  [x] Bot Difficulty : The difficulty of the bot (% chance of picking the right answer out of 100).
#  == (Network Settings) ==
#  [ ] Server Name : The name of the server.
#  [x] Server Port : The port of the server (1234 by default).
#  [ ] Max Players : The maximum amount of players.
#  == (Single Player Settings) ==
#  [x] How many players : The amount of players.
#  [x] How many bots : The amount of bots.
#  == (Quiz Settings) ==
#  [x] Quiz Category : The category of the quiz.
#  [x] Quiz Difficulty : The difficulty of the quiz.
#  [x] Question Amount : The amount of questions.
#  [x] Question Type : The type of questions (True/False, Multi choice).
#  == (Player Settings) ==
#  [x] Player Name : The name of the player.
#  [x] Player Colour : The colour of the player.
#  [ ] Player Icon : The icon of the player (GUI Only).

# - - - - - - - Imports - - - - - - -#
import os
import threading
import time
import html
import random

from Maxs_Modules.files import SaveFile, load_questions_from_file
from Maxs_Modules.network import get_ip, QuizGameServer, QuizClient, QuizGameClient
from Maxs_Modules.setup import UserData
from Maxs_Modules.tools import try_convert, set_if_none, get_user_input_of_type, strBool, sort_multi_array
from Maxs_Modules.debug import debug_message, error
from Maxs_Modules.renderer import Menu, divider, Colour

# - - - - - - - Variables - - - - - - -#
data_folder = "UserData/Games/"
category_offset = 9
max_number_of_questions = 50
quiz_categories = ["General Knowledge", "Books", "Film", "Music", "Musicals & Theatres", "Television", "Video Games",
                   "Board Games", "Science & Nature", "Computers", "Mathematics", "Mythology", "Sports", "Geography",
                   "History", "Politics", "Art", "Celebrities", "Animals", "Vehicles", "Comics", "Gadgets",
                   "Japanese Anime & Manga", "Cartoon & Animations"]
host_a_server_by_default = True


# - - - - - - - Functions - - - - - - -#


def generate_new_save_file():
    """
    Generates a new save file name by searching through the data folder for a name that is not already taken
    (most likely: Game_X.json)

    @return: The name of the save file
    """
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
    """
    Gets a list of all the saved games (note this returns a list of all JSON files in the data folder and if a user
    has tampered with the data folder, a JSON file that isn't a save file may be returned)

    @return: A list of all the saved games
    """
    # Get a list of all the files in the data folder
    files = os.listdir(data_folder)
    debug_message("Files in data folder: " + str(files), "Game")

    # Remove all the files that are not .json files
    for file in files:
        if not file.endswith(".json"):
            files.remove(file)

    return files


# - - - - - - - Classes - - - - - - -#


class Question:
    category = None
    type = None  # Although type is a reserved word, it is used in the API and is therefore used here
    difficulty = None
    question = None
    correct_answer = None
    incorrect_answers = None

    def __init__(self) -> None:
        pass

    def load(self, data: dict) -> None:
        """
        Loads the data from the API into the question object
        @param data: The data from the API
        """
        self.category = data.get("category")
        self.type = data.get("type")
        self.difficulty = data.get("difficulty")
        self.question = html.unescape(data.get("question"))

        self.correct_answer = html.unescape(data.get("correct_answer"))
        self.incorrect_answers = data.get("incorrect_answers")

        # Unescape the incorrect answers
        for i in range(len(self.incorrect_answers)):
            self.incorrect_answers[i] = html.unescape(self.incorrect_answers[i])


class User:
    # Game Variables
    player_type = "User"
    name = None
    colour = None
    icon = None
    points = 0
    correct = 0
    incorrect = 0
    streak = 0
    highest_streak = 0
    questions_missed = 0
    answers = []
    times = []

    # Calculated Stats
    questions_answered = 0
    average_time = 0
    average_time_correct = 0
    average_time_incorrect = 0
    average_time_missed = 0
    accuracy = 0

    # States
    is_host = False
    is_connected = False
    has_answered = False

    def __int__(self, name: str, colour: str, icon: str) -> None:
        """
        Creates a new user
        @param name: The name of the user
        @param colour: The colour of the user
        @param icon: The path to the icon of the user
        """
        self.name = name
        self.colour = colour
        self.icon = icon

    def load(self, data: dict) -> None:
        # Game Variables
        self.name = data.get("name")
        self.colour = data.get("colour")
        self.icon = data.get("icon")
        self.points = data.get("points")
        self.correct = data.get("correct")
        self.incorrect = data.get("incorrect")
        self.streak = data.get("streak")
        self.highest_streak = data.get("highest_streak")
        self.questions_missed = data.get("questions_missed")
        self.answers = data.get("answers")
        self.times = data.get("times")

        # States
        self.has_answered = data.get("has_answered")

        self.load_defaults()

    def load_defaults(self) -> None:
        """
        Loads the default values for the user, should any of the values be None.
        """
        self.name = set_if_none(self.name, "Player")
        self.colour = set_if_none(self.colour, "White")
        self.icon = set_if_none(self.icon, "X")
        self.points = set_if_none(self.points, 0)
        self.correct = set_if_none(self.correct, 0)
        self.incorrect = set_if_none(self.incorrect, 0)
        self.streak = set_if_none(self.streak, 0)
        self.highest_streak = set_if_none(self.highest_streak, 0)
        self.questions_missed = set_if_none(self.questions_missed, 0)
        self.answers = set_if_none(self.answers, [])
        self.times = set_if_none(self.times, [])

        # States
        self.has_answered = set_if_none(self.has_answered, False)

    def calculate_stats(self) -> None:
        """
        Calculates the stats for the user, this saves time as the stats only need to be calculated when the user selects
        to display them
        """

        # Simple stats
        self.questions_answered = self.correct + self.incorrect

        # Dont divide by 0
        if self.questions_answered != 0:
            self.accuracy = self.correct / self.questions_answered

        # Add all the times together and then divide by the length to get the mean
        if len(self.times) != 0:
            self.average_time = sum(self.times) / len(self.times)

        # Loop through the answers and times and calculate the average time for correct and incorrect answers
        time_correct = []
        time_incorrect = []
        time_missed = []

        for i in range(len(self.answers)):
            if self.answers[i] == "Correct":
                time_correct.append(self.times[i])
            elif self.answers[i] == "Incorrect":
                time_incorrect.append(self.times[i])
            elif self.answers[i] == "Missed_Correct" or self.answers[i] == "Missed_Incorrect":
                time_missed.append(self.times[i])

        # Calculate the average time for correct incorrect and missed answers (skip if zero as that causes a divide by
        # zero error)
        if len(time_correct) != 0:
            self.average_time_correct = sum(time_correct) / len(time_correct)
        if len(time_incorrect) != 0:
            self.average_time_incorrect = sum(time_incorrect) / len(time_incorrect)
        if len(time_missed) != 0:
            self.average_time_missed = sum(time_missed) / len(time_missed)

    def show_stats(self) -> None:
        """
        Prints the collected stats variables to the console
        """

        # Calculate any stats that arent just supplied by the game
        self.calculate_stats()

        # Print the stats
        print(self.styled_name() + "'s Stats: ")
        print("Type: " + self.player_type)
        print("Score: " + str(self.points))
        print("Streak: " + str(self.streak))
        print("Highest Streak: " + str(self.highest_streak))
        print("Questions Answered: " + str(self.questions_answered))
        print("Questions Correct: " + str(self.correct))
        print("Questions Incorrect: " + str(self.incorrect))
        print("Questions Skipped: " + str(self.questions_missed))
        print("Average Time: " + str(self.average_time))
        print("Average Time Correct: " + str(self.average_time_correct))
        print("Average Time Incorrect: " + str(self.average_time_incorrect))
        print("Average Time Skipped: " + str(self.average_time_missed))
        print("Accuracy: " + str(self.accuracy * 100) + "%")

    def reset(self) -> None:
        """
        Removes all the set answers, 0s out the points, correct, incorrect, steak, questions_missed variables. Name,
        icon and colour are kept
        """

        # Clear the arrays
        self.answers.clear()
        self.times.clear()

        # Zero out the vars
        self.points = 0
        self.correct = 0
        self.incorrect = 0
        self.streak = 0
        self.questions_missed = 0

        # An alternative way to do this is to None the vars and then call load_defaults()

    def styled_name(self) -> str:
        """
        Returns the name of the user with the colour (includes reset char)
        @return: The name of the user with the colour (includes reset char)
        """
        return self.colour + self.name + Colour.RESET


class Bot(User):
    accuracy = 0.5

    def __int__(self, name: str, colour: str, icon: str, accuracy: float) -> None:
        """
        Creates a new bot and assigns it a name, colour and icon
        @param name: The name of the bot
        @param colour: The colour of the bot
        @param icon: The path to the icon of the bot
        @param accuracy: How likely the bot is to get the question correct
        """
        self.accuracy = accuracy

        # Set up the user
        super().__int__(name, colour, icon)

    def load(self, data: dict) -> None:
        super().load(data)
        self.accuracy = data.get("accuracy")
        self.load_defaults()

    def load_defaults(self) -> None:
        super().load_defaults()
        self.accuracy = set_if_none(self.accuracy, 0.5)
        self.player_type = "Bot"

    def show_stats(self) -> None:
        """
        Prints the collected stats variables to the console
        """
        # Ensure that calculations dont mess with accuracy
        save_accuracy = self.accuracy

        # Calculate the stats
        super().show_stats()

        # Reset the accuracy
        self.accuracy = save_accuracy

        # Print the stats
        print("Accuracy (EXPECTED): " + str(self.accuracy * 100) + "%")

    def answer(self, question: Question) -> str:
        """
        Using the accuracy, the bot will return the correct answer if random.random() is less than the accuracy,
        otherwise it will return a random incorrect answer

        @param question: The question object where the bot should get its answer from
        @return: The answer the bot chose
        """

        # Check if the bot got the question correct
        correct = random.random() < self.accuracy

        if correct:
            return question.correct_answer
        else:
            return random.choice(question.incorrect_answers)


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
    points_multiplier_for_a_streak_base = None
    compounding_amount_for_a_streak = None
    randomise_questions = None
    randomise_answer_placement = None
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
    current_user_playing_net_name = None
    online_enabled = None
    game_finished = None
    joined_game = None
    game_started = False

    # API Conversion
    api_category = None
    api_type = None

    # Game data
    users = None
    questions = None
    bots = None
    backend = None
    server_thread = None

    def __init__(self, quiz_save: str = None) -> None:
        """
        Creates a new game. If the quiz save is not none, then load the quiz save because the user wants to continue a
        game otherwise generate a new save file.

        @param quiz_save:
        """
        # Call the super class and pass the save file name, this will automatically load the settings

        # If the quiz save is not none, then load the quiz save because the user wants to continue a game otherwise
        # generate a new save file
        if quiz_save is not None:
            super().__init__(data_folder + quiz_save)
        else:
            super().__init__(data_folder + generate_new_save_file())

        # Set the online enabled variable, note it is not saved because the online state can change between runs
        usersettings = UserData()
        self.online_enabled = usersettings.network

        # Load the save data into variables
        self.load_from_saved()

        # Set the default settings if the settings are none
        self.set_settings_default()

        # Convert everything back
        self.convert_all_from_save_data()

    def load_from_saved(self) -> None:
        """
        Loads the game's variables from the saved data (self.save_data)
        """
        # Load User Settings
        self.host_a_server = try_convert(self.save_data.get("host_a_server"), bool)
        self.time_limit = try_convert(self.save_data.get("time_limit"), int)
        self.show_score_after_question_or_game = try_convert(self.save_data.get("show_score_after_question_or_game"),
                                                             str)
        self.show_correct_answer_after_question_or_game = try_convert(
            self.save_data.get("show_correct_answer_after_question_or_game"), str)
        self.points_for_correct_answer = try_convert(self.save_data.get("points_for_correct_answer"), int)
        self.points_for_incorrect_answer = try_convert(self.save_data.get("points_for_incorrect_answer"), int)
        self.points_for_no_answer = try_convert(self.save_data.get("points_for_no_answer"), int)
        self.points_multiplier_for_a_streak = try_convert(self.save_data.get("points_multiplier_for_a_streak"), int)
        self.points_multiplier_for_a_streak_base = try_convert(
            self.save_data.get("points_multiplier_for_a_streak_base"), int)
        self.compounding_amount_for_a_streak = try_convert(self.save_data.get("compounding_amount_for_a_streak"), int)
        self.randomise_questions = try_convert(self.save_data.get("randomise_questions"), bool)
        self.randomise_answer_placement = try_convert(self.save_data.get("randomise_answer_placement"), bool)
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
        self.game_finished = try_convert(self.save_data.get("game_finished"), bool)
        self.joined_game = try_convert(self.save_data.get("joined_game"), bool)

        # Load Game Data
        self.users = try_convert(self.save_data.get("users"), list)
        self.questions = try_convert(self.save_data.get("questions"), list)
        self.bots = try_convert(self.save_data.get("bots"), list)

    def set_settings_default(self) -> None:
        """
        Sets the default settings if the settings are none
        """
        # User Chosen Settings
        self.host_a_server = set_if_none(self.host_a_server, host_a_server_by_default)
        self.time_limit = set_if_none(self.time_limit, 10)
        self.show_score_after_question_or_game = set_if_none(self.show_score_after_question_or_game, "Question")
        self.show_correct_answer_after_question_or_game = set_if_none(self.show_correct_answer_after_question_or_game,
                                                                      "Question")
        self.points_for_correct_answer = set_if_none(self.points_for_correct_answer, 1)
        self.points_for_incorrect_answer = set_if_none(self.points_for_incorrect_answer, -1)
        self.points_for_no_answer = set_if_none(self.points_for_no_answer, 0)
        self.points_multiplier_for_a_streak = set_if_none(self.points_multiplier_for_a_streak, 1.1)
        self.points_multiplier_for_a_streak_base = set_if_none(self.points_multiplier_for_a_streak_base, 1.1)
        self.randomise_questions = set_if_none(self.randomise_questions, True)
        self.randomise_answer_placement = set_if_none(self.randomise_answer_placement, True)
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
        self.game_finished = set_if_none(self.game_finished, False)
        self.joined_game = set_if_none(self.joined_game, False)

        # Game Data
        self.users = set_if_none(self.users, [])
        self.bots = set_if_none(self.bots, [])
        self.questions = set_if_none(self.questions, [])

    # __ DATA RELATED FUNCTIONS __

    def set_settings(self) -> None:
        """
        Shows the user various menus related to settings, allowing them to change the settings
        """
        self.settings_gameplay()

    def convert_users(self) -> None:
        """
        Converts the users list from a list of dicts to a list of User objects
        
        @return: This function returns if the list is empty or if the first item is already a User object
        """
        # Check if the users list is empty
        if len(self.users) == 0:
            return

        # For each user in the list of users convert the dict to a User object using the load() function
        for x in range(len(self.users)):
            # Check if the user is already a User object
            if type(self.users[x]) is User:
                continue

            print(f"Converting user {x} to a User object")

            # Load
            user_object = User()
            user_object.load(self.users[x])
            self.users[x] = user_object

    def convert_bots(self) -> None:
        """
        Converts the bots list from a list of dicts to a list of Bot objects

        @return: This function returns if the list is empty or if the first item is already a Bot object
        """
        # Check if the bots list is empty
        if len(self.bots) == 0:
            return

        # Check if the bot is already a Bot object
        if type(self.bots[0]) is Bot:
            return

        # For each bot in the list of bots convert the dict to a Bot object using the load() function
        for x in range(len(self.bots)):
            bot_object = Bot()
            bot_object.load(self.bots[x])
            self.bots[x] = bot_object

    def set_users(self) -> None:
        """
        Gets the user to enter the names and colours for each user and then creates each bot
        """
        user_id = 0
        while user_id != self.how_many_players:

            # Clear the screen
            os.system("cls")

            # Create a new user
            user_id += 1
            user = User()

            # Get name and check if it is valid
            while user.name is None:
                user.name = try_convert(input("Enter the name for user " + str(user_id) + ": "), str)

            # Get colour
            colour_menu = Menu("Choose a colour for " + user.name, Colour.colours_names_list)
            colour_menu.get_input()
            user.colour = Colour.colours_list[Colour.colours_names_list.index(colour_menu.user_input)]

            if user.name == "Max":
                user.colour += Colour.BLINK

            # Add to list of users
            self.users.append(user)

            # Create the bots
            for x in range(self.how_many_bots):
                bot = Bot()
                bot.name = "Bot " + str(x + 1)
                bot.colour = Colour.GREY + Colour.ITALIC
                bot.accuracy = self.bot_difficulty / 100
                self.bots.append(bot)

    def get_questions(self) -> None:
        """
        Gets the questions from the API or from the file depending on the online_enabled setting. Afterward it converts
        the questions into Question objects and then shuffles the questions if the randomise_questions setting is True.
        Finally, it saves the questions to the file.
        """
        # Check if the user is online
        if self.online_enabled:

            print("Getting questions from the internet...")

            # Import the api_get_questions function, this is only imported if the user is online as it is not needed
            # if the user is offline and don't want to run the requests installation
            from Maxs_Modules.network import api_get_questions

            # Convert the settings to the api syntax
            self.convert_question_settings_to_api()

            # Use the api to get the questions
            self.questions = api_get_questions(self.question_amount, self.api_category, self.quiz_difficulty,
                                               self.api_type)

        else:

            print("Loading questions from file...")

            # Load the question from the saved questions
            self.questions = load_questions_from_file()

        debug_message("Questions: " + str(self.questions), "Game")

        # Convert the data into a list of Question objects
        self.convert_questions()

        # Save the questions to the file
        self.save()

    def convert_question_settings_to_api(self) -> None:
        """
        Since the API uses indices for the categories and lowercase strings for the types, this function converts the
        user set settings into syntax that the API can understand
        """
        # Convert the category if it is not any
        if self.quiz_category != "Any":
            # Get the index of the question type
            category_index = quiz_categories.index(self.quiz_category)

            # Add the offset to the index. This is because the api starts at 9 and not 0 (ends at 32)
            self.api_category = category_index + category_offset

        print("Category: " + str(self.api_category))

        # Convert the type if it is not any
        if self.question_type != "Any":

            match self.question_type:
                case "Multiple Choice":
                    self.api_type = "multiple"
                case "True/False":
                    self.api_type = "boolean"

    def convert_questions(self) -> None:
        """
        Converts the questions list from a list of dicts to a list of Question objects

        @return: This function returns if the list is empty or if the first item is already a Question object
        """
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

    # __ GAME FUNCTIONS __

    def begin(self) -> None:
        """
        Starts the game by printing all the users and then getting the questions if there are none
        """
        for user in self.users:
            print(user.styled_name())

        # If there are no questions then get them
        if len(self.questions) == 0:
            self.get_questions()

        # Shuffle the questions if the user wants to
        if self.randomise_questions:
            random.shuffle(self.questions)

        if self.host_a_server:
            self.wait_for_players()

        # Start the game, check if the game has finished or play the game
        if self.check_game_finished():
            # If the game has finished then show the results
            self.game_end()
        else:
            self.play()

    def show_scores(self) -> None:
        """
        Shows the scores of all the players, and then shows the stats of the player selected
        """
        # Array to store the names and scores
        score_menu_players = []
        score_menu_scores = []

        # Add the users and their scores to the arrays
        for user in self.users:
            score_menu_players.append(user.styled_name())
            score_menu_scores.append(user.points)

        # Add the bots and their scores to the arrays
        for bot in self.bots:
            score_menu_players.append(bot.styled_name())
            score_menu_scores.append(bot.points)

        # Sort the arrays based on the scores
        score_menu_multi = [score_menu_players, score_menu_scores]
        debug_message("Score menu multi unsorted: " + str(score_menu_multi), "Game")
        score_menu_multi = sort_multi_array(score_menu_multi, True)
        debug_message("Score menu multi sorted: " + str(score_menu_multi), "Game")

        # Convert the scores to strings
        for x in range(len(score_menu_multi[1])):
            score_menu_multi[1][x] = str(score_menu_multi[1][x])

        # Add the next option (has to be after sort as "Game Finished/Next Question" is added to the end and also
        # causes errors becuase they are not ints)
        score_menu_multi[0].append("Next")
        if self.game_finished:
            score_menu_multi[1].append("Game Finished")
        else:
            score_menu_multi[1].append("Next Question")

        # Show the menu
        score_menu = Menu("Scores", score_menu_multi, True)
        score_menu.get_input()

        # If the user selected a user then show their stats
        if score_menu.user_input != "Next":

            # Find the user selected
            for user in self.users:

                # If the user is found then show their stats
                if user.styled_name() == score_menu.user_input:
                    user.show_stats()

                    # Give time for the user to read the stats
                    input("Press enter to continue...")
                    self.show_scores()

            # Find the bot selected
            for bot in self.bots:

                # If the bot is found then show their stats
                if bot.styled_name() == score_menu.user_input:
                    bot.show_stats()

                    # Give time for the user to read the stats
                    input("Press enter to continue...")
                    self.show_scores()

    def show_question_markings(self) -> None:
        """
        Shows the answer each player submited for the questions. It begins at current_question and then goes through each
        question after that, so when called best practice is to set current_question to 0
        """

        # Get the current question
        question = self.questions[self.current_question]

        # Array to store the names and answers
        marking_menu_players = []
        marking_menu_answers = []

        # Loop through each user adding their name and answer to the arrays
        for user in self.users:
            marking_menu_players.append(user.styled_name())

            # Check if the user answered all the questions, if not there is an error
            if len(user.answers) < self.current_question:
                marking_menu_answers.append("ERROR")
            else:
                marking_menu_answers.append(user.answers[self.current_question])

        # Loop through each bot adding their name and answer to the arrays
        for bot in self.bots:
            marking_menu_players.append(bot.styled_name())

            # Check if the bot answered all the questions, if not there is an error
            if len(bot.answers) < self.current_question:
                marking_menu_answers.append("ERROR")
            else:
                marking_menu_answers.append(bot.answers[self.current_question])

        # Add the correct answer
        marking_menu_players.append("Correct Answer")
        marking_menu_answers.append(question.correct_answer)

        # Add the next and skip option
        marking_menu_players.append("Next Question")
        marking_menu_answers.append("Game Finished")

        # Show the menu
        marking_menu = Menu("Question: " + question.question, [marking_menu_players, marking_menu_answers], True)
        marking_menu.get_input()

        # Note to self, because python is python with its syntax, the "_" is what default is
        match marking_menu.user_input:
            case "Next Question":
                if self.current_question == len(self.questions) - 1:
                    return

                # If there are any questions left to overview then show the next question
                else:
                    self.current_question += 1
                    self.show_question_markings()

            case "Correct Answer":
                print("These players got the question correct: ")

                # Show all the users that got the question correct
                for user in self.users:
                    if user.answers[self.current_question] == question.correct_answer:
                        print(user.styled_name())

                # Give time for the user to read the correct users
                input("Press enter to continue...")
                self.show_question_markings()

            case _:
                # Find the user selected
                for user in self.users:

                    # If the user is found then show their stats
                    if user.styled_name() == marking_menu.user_input:
                        user.show_stats()

                        # Give time for the user to read the stats
                        input("Press enter to continue...")
                        self.show_question_markings()

                # Find the bot selected
                for bot in self.bots:

                    # If the bot is found then show their stats
                    if bot.styled_name() == marking_menu.user_input:
                        bot.show_stats()

                        # Give time for the user to read the stats
                        input("Press enter to continue...")
                        self.show_question_markings()

    def mark_question(self, user_input, current_user) -> None:
        """
        Marks the question and updates the user class based on the mark

        @param user_input: The answer submitted by the user
        @param current_user: The user that answered the question, and where the points will be added to
        """
        # Get the current question
        question = self.questions[self.current_question]

        debug_message(current_user.player_type + " " + current_user.name + " answered: " + user_input, "Game")

        # Check if the answer is correct
        if user_input == question.correct_answer:

            # Tell the user that the answer is correct
            if current_user.player_type == "User":
                print("Correct!")

            # Add the answer to the user
            current_user.answers[len(current_user.answers) - 1] += "Correct"

            # Set the point to the default point
            point = self.points_for_correct_answer

            # Check if the user has a streak
            if current_user.streak > 0:
                # Compound the streak
                self.points_multiplier_for_a_streak *= self.compounding_amount_for_a_streak

                # If the user has a streak then add the streak to the point
                point = self.points_multiplier_for_a_streak * current_user.streak

            # If the answer is correct then add a point to the user
            current_user.points += point

            # Add a point to the streak
            current_user.streak += 1
            if current_user.streak > current_user.highest_streak:
                current_user.highest_streak = current_user.streak

            # Add correct
            current_user.correct += 1

        else:
            if current_user.player_type == "User":
                print("Incorrect.")
                if self.show_correct_answer_after_question_or_game:
                    print("The correct answer was: " + question.correct_answer)

            # Add the answer to the user
            current_user.answers[len(current_user.answers) - 1] += "Incorrect"

            # Reset the streak
            current_user.streak = 0
            self.points_multiplier_for_a_streak = self.points_multiplier_for_a_streak_base

            # Add incorrect
            current_user.incorrect += 1

            # If the answer is not correct then remove a point from the user
            current_user.points += self.points_for_incorrect_answer

    def play(self) -> None:
        """
        Shows the user the question and then gets the user to answer it in the specified time by using a different
        thread for the user input. Then it marks the question and calculates the score for the player. Afterwards it
        runs the next question
        """
        # If its a networked game then get the local player as the sync overrides it
        if self.joined_game:
            # Loop through the users trying to find the saved name
            for user_index in range(len(self.users)):
                if self.users[user_index].name == self.current_user_playing_net_name:
                    self.current_user_playing = user_index

        # Save the users progress
        self.save()

        # Get the current question & user
        question = self.questions[self.current_question]
        current_user = self.users[self.current_user_playing]

        # Create options
        options = question.incorrect_answers.copy()
        options.append(question.correct_answer)

        # Shuffle the options
        if self.randomise_answer_placement:
            random.shuffle(options)

        # Create the question menu
        question_menu = Menu(question.question, options)

        # Clear the screen
        question_menu.clear()

        # Print some info
        print(divider)
        print("Question " + str(self.current_question + 1) + " of " + str(self.question_amount))
        print("User: " + current_user.styled_name())
        print("Time Limit: " + str(self.time_limit) + " seconds")

        # Don't clear the screen as information is printed before the menu
        question_menu.clear_screen = False

        # Timings
        start_time = time.time()

        # Show the question and get the user input
        question_menu.time_limit = self.time_limit
        question_menu.get_input()

        if question_menu.user_input is not None:
            # As the user didn't miss then just leave the preheader blank
            current_user.answers.append("")

            # Mark the question
            self.mark_question(question_menu.user_input, current_user)

        else:
            # If the game should pick a random question when the time runs out
            if self.pick_random_question:
                # Add the Missed part to the user
                current_user.answers.append("Missed_")

                # Get a random option
                random_option = random.choice(options)
                print("Auto picking: " + random_option)
                self.mark_question(random_option, current_user)

            else:
                # Add the points for no answer
                current_user.answers.append("Missed_Incorrect")
                current_user.points += self.points_for_no_answer

            # Add missed question to the user
            current_user.questions_missed += 1

            print("\nTime's up!")

        # Store the time data
        end_time = time.time() - start_time
        debug_message("Time taken: " + str(end_time) + " seconds", "Game")
        current_user.times.append(end_time)

        # Make the bots answer
        for bot in self.bots:
            # Get the bot to answer the question
            bot_answer = bot.answer(question)

            # As the bot cant miss then just leave the preheader blank
            bot.answers.append("")

            # Mark the question
            self.mark_question(bot_answer, bot)

            # Add the time, for use in stats
            bot.times.append(0)

        # Give user time to read the answer
        time.sleep(3)

        # Move onto the next question
        self.next_question()

    def next_question(self) -> None:
        """
        Moves onto the next question. If the game has finished then it shows the results.
        """
        # Move onto the next question
        self.current_question += 1

        # Question is answered
        self.users[self.current_user_playing].has_answered = True

        # Check if backed is a server object
        is_server = isinstance(self.backend, QuizGameServer)
        is_client = isinstance(self.backend, QuizGameClient)

        # If this is the server then sync the game
        if is_server:
            print("Waiting for all players to answer...")

            # Wait for all players to answer
            while True:
                waiting = False

                # Loop through the users until one is found that hasn't answered
                for user in self.users:
                    if user.has_answered is False:
                        waiting = True
                        print(f"Waiting for {user.name} to answer...")

                if not waiting:
                    break
                else:
                    time.sleep(.5)

            debug_message("All players have answered", "Game")

            # Moved on so reset question state
            self.users[self.current_user_playing].has_answered = False

            # Sync the players and bots (.5 seconds so the messages are separate)
            self.backend.sync_players()
            time.sleep(.5)
            self.backend.sync_bots()
            time.sleep(.5)
            self.backend.send_message_to_all("Move on to: game finished / show scores / next question", "move_on")

        # If this is a client then wait for the server to sync and all players to answer
        elif is_client:
            # Send the users answer to the server
            self.backend.send_self()

            print("Waiting for server to move on...")
            # Wait for all players to answer
            self.backend.wait_for_move_on()

            # Moved on so reset question state
            self.users[self.current_user_playing].has_answered = False
            if is_client:
                self.backend.send_self()

        # Check if the game has finished
        if self.check_game_finished():
            # If the game has finished then show the results
            self.game_end()
            return

        if self.show_score_after_question_or_game == "Question":
            # Show the score
            self.show_scores()

        # Move onto the question
        self.play()

    def check_game_finished(self) -> bool:
        """
        Checks if the game has finished
        @return: True if the game has finished
        """

        debug_message("Checking if game has finished: " + str(self.current_question) + " of " + str(
            len(self.questions)) + " questions",
                      "Game")

        # Check if the game has finished
        if self.current_question == len(self.questions):

            # Check if it is another user's turn (only if there is not a multiplayer game)
            if self.current_user_playing < len(self.users) - 1 and self.backend is None:
                # If it is another user's turn then move onto the next user
                self.current_user_playing += 1
                self.current_question = 0

                # Move onto the next question
                self.play()
                self.game_finished = False
            else:
                self.game_finished = True
        else:
            self.game_finished = False

        return self.game_finished

    def game_end(self) -> None:
        """
        Runs when the game ends
        """
        # Save that the game has ended
        self.save()

        # Create the game end menu
        game_end_menu = Menu("Game Finished", ["Compare Scores", "Compare User Answers", "Finish"])
        game_end_menu.get_input()

        # Check what the user selected
        match game_end_menu.user_input:
            case "Compare Scores":
                self.show_scores()
                self.game_end()
            case "Compare User Answers":
                self.current_question = 0
                self.show_question_markings()
                self.game_end()
            case "Finish":
                return

    def reset(self) -> None:
        """
        Resets the game back to a state that allows the game to be played again from the start. This will clear all user
         data but all settings and questions will be kept
        """

        # Reset the current question
        self.current_question = 0

        # Reset the current user playing
        self.current_user_playing = 0

        # Reset the game finished variable
        self.game_finished = False

        # Reset the users
        for user in self.users:
            user.reset()

        # Save the game
        self.save()

    def prepare_save_data(self) -> None:
        """
        Prepares the save data for the game by converting the classes to dicts and removing the socket and thread
        """
        # Create the save data for the UserSettings object
        self.save_data = self.__dict__.copy()

        # Convert the user class to a dict
        for user_index in range(len(self.users)):
            # Check if the user is not already a dict (have to use isinstance as if it is a dict then user_index wont
            # work)
            if isinstance(self.users[user_index], User):
                # Convert the user to a dict
                self.users[user_index] = self.users[user_index].__dict__

        # Convert the question class to a dict
        for question_index in range(len(self.questions)):
            # Check if the question is a class
            if type(self.questions[question_index]) == Question:
                self.save_data["questions"][question_index] = self.questions[question_index].__dict__

        # Conver the bots to a dict
        for bot_index in range(len(self.bots)):
            # Check if the bot is a class
            if type(self.bots[bot_index]) == Bot:
                self.save_data["bots"][bot_index] = self.bots[bot_index].__dict__

        # Remove the thread and socket
        try:
            del self.save_data["backend"]
        except KeyError:
            pass

        try:
            del self.save_data["server_thread"]
        except KeyError:
            pass

    def save(self) -> None:
        """
        Saves the game data to the file. Converts the user and question objects to dicts before saving and then
        converts them back once written to the JSON file
        """
        self.prepare_save_data()

        # Call the super class save function
        super().save()

        # Convert everything back
        self.convert_all_from_save_data()

    def convert_all_from_save_data(self) -> None:
        self.convert_users()
        self.convert_questions()
        self.convert_bots()

    # __ MENUS __

    def settings_local(self) -> None:
        """
        Shows a menu to configure the settings for a local hosted game
        """
        local_menu_options = ["How many players", "Next"]
        local_menu_values = [str(self.how_many_players), "Questions Settings"]
        single_player_menu = Menu("Game Settings: Local", [local_menu_options, local_menu_values], True)
        single_player_menu.get_input()

        match single_player_menu.user_input:
            case "How many players":
                self.how_many_players = get_user_input_of_type(int, "How many players")

        # Loop if they chose to modify the settings, do not loop if they chose to go to next menu
        if single_player_menu.user_input != "Next":
            self.settings_local()
        else:
            self.set_users()

    def settings_networking(self) -> None:
        """
        Shows a menu to configure the networking settings for the game

        """
        networking_menu_options = ["Server Name", "Server Port", "Max Players", "Next"]
        networking_menu_values = [str(self.server_name), str(self.server_port), str(self.max_players),
                                  "Questions Settings"]

        networking_menu = Menu("Game Settings: Networking", [networking_menu_options, networking_menu_values], True)
        networking_menu.get_input()

        match networking_menu.user_input:

            case "Server Name":
                self.server_name = get_user_input_of_type(str, "Server Name")

            case "Server Port":
                self.server_port = get_user_input_of_type(int, "Server Port")

            case "Max Players":
                self.max_players = get_user_input_of_type(int, "Max Players")

        # Loop if they chose to modify the settings, do not loop if they chose to go to next menu
        if networking_menu.user_input != "Next":
            self.settings_networking()

    def settings_gameplay(self) -> None:
        """
        Shows a menu to configure the gameplay settings for the game
        """
        game_play_menu_options = ["Host a server", "Time limit", "Question Amount", "Category", "Difficulty", "Type",
                                  "Show score after Question/Game", "Show correct answer after Question/Game",
                                  "Points for correct answer", "Points for incorrect answer",
                                  "Points for no answer", "Points multiplier for a streak",
                                  "Compounding amount for a streak", "Randomise questions",
                                  "Randomise answer placement",
                                  "Pick random question when run out of time",
                                  "Bot difficulty", "Number of bots", "Next"]

        game_play_menu_values = [str(self.host_a_server), str(self.time_limit), str(self.question_amount),
                                 str(self.quiz_category), str(self.quiz_difficulty), str(self.question_type),
                                 str(self.show_score_after_question_or_game),
                                 str(self.show_correct_answer_after_question_or_game),
                                 str(self.points_for_correct_answer), str(self.points_for_incorrect_answer),
                                 str(self.points_for_no_answer),
                                 str(self.points_multiplier_for_a_streak), str(self.compounding_amount_for_a_streak),
                                 str(self.randomise_questions), str(self.randomise_answer_placement),
                                 str(self.pick_random_question),
                                 str(self.bot_difficulty), str(self.how_many_bots)]

        if self.host_a_server:
            game_play_menu_values.append("Networking Settings")
        elif not self.host_a_server:
            game_play_menu_values.append("Local Settings")

        gameplay_menu = Menu("Game Settings: Gameplay", [game_play_menu_options, game_play_menu_values], True)
        gameplay_menu.get_input()

        match gameplay_menu.user_input:
            case "Host a server":
                self.host_a_server = get_user_input_of_type(strBool,
                                                            "Host a server (" + Colour.true_or_false_styled() + ")")

            case "Time limit":
                self.time_limit = get_user_input_of_type(int, "Time limit (seconds)")

            case "Question Amount":
                self.question_amount = get_user_input_of_type(int, "Question Amount (1-50)", range(1, 51))

            case "Category":
                category_menu = Menu("Category", quiz_categories)
                category_menu.get_input()
                self.quiz_category = category_menu.user_input

            case "Difficulty":
                self.quiz_difficulty = get_user_input_of_type(str, "Difficulty (Easy, Medium, Hard)", ["Easy", "Medium",
                                                                                                       "Hard"])

            case "Type":
                self.question_type = get_user_input_of_type(str, "Type (Multiple, True/False)", ["Multiple",
                                                                                                 "True/False"])

            case "Show score after Question/Game":
                self.show_score_after_question_or_game = get_user_input_of_type(str,
                                                                                "Show score after: (Question/Game)",
                                                                                ["Question", "Game"])

            case "Show correct answer after Question/Game":
                self.show_correct_answer_after_question_or_game = get_user_input_of_type(str,
                                                                                         "Show correct answer "
                                                                                         "after: (Question/Game)",
                                                                                         ["Question", "Game"])

            case "Points for correct answer":
                self.points_for_correct_answer = get_user_input_of_type(int, "Points for correct answer")

            case "Points for incorrect answer":
                self.points_for_incorrect_answer = get_user_input_of_type(int, "Points for incorrect answer")

            case "Points for no answer":
                self.points_for_no_answer = get_user_input_of_type(int, "Points for no answer")

            case "Points multiplier for a streak":
                self.points_multiplier_for_a_streak = get_user_input_of_type(int, "Points multiplier for a streak")

            case "Compounding amount for a streak":
                self.compounding_amount_for_a_streak = get_user_input_of_type(int, "Compounding amount for a streak")

            case "Randomise questions":
                self.randomise_questions = get_user_input_of_type(strBool, "Randomise questions ("
                                                                  + Colour.true_or_false_styled() + ")")

            case "Randomise answer placement":
                self.randomise_answer_placement = get_user_input_of_type(strBool,
                                                                         "Randomise answer placement ("
                                                                         + Colour.true_or_false_styled() + ")")

            case "Pick random question when run out of time":
                self.pick_random_question = get_user_input_of_type(strBool, "Pick random question (" +
                                                                   Colour.true_or_false_styled() + ")")

            case "Bot difficulty":
                self.bot_difficulty = get_user_input_of_type(int, "Bot difficulty (%)", range(1, 101))

            case "Number of bots":
                self.how_many_bots = get_user_input_of_type(int, "Number of bots")

            case "Next":
                if self.host_a_server:
                    self.settings_networking()
                elif not self.host_a_server:
                    self.settings_local()

        # Loop if they chose to modify the settings, do not loop if they chose to go to next menu
        if gameplay_menu.user_input != "Next":
            self.settings_gameplay()

    def wait_for_players(self):
        """
        Waits for players to join the server
        """

        # Set up the host (if there isn't one already) (host is always the first user in the list)
        if len(self.users) == 0:
            self.set_users()
        self.users[0].is_host = True
        self.users[0].is_connected = True

        # Create a socket
        try:
            self.backend = QuizGameServer(get_ip(), self.server_port)
            self.backend.game = self
        except OSError:
            error("Could not create a socket. Please try again.")
            self.settings_networking()
            return

        # Thread the server
        self.server_thread = threading.Thread(target=self.backend.run)
        self.server_thread.start()

        debug_message("Server started on " + get_ip() + ":" + str(self.server_port) + "!", "game_server")

        # Wait for players to join
        self.game_started = False
        self.backend.running = True
        while True:
            ip_text = f"Server IP: {get_ip()}:{self.server_port}"
            players = [ip_text]

            # Convert any users that have been added in
            self.convert_users()

            # Loop through all the users
            for user in self.users:
                # Add them to the list
                players.append(user.styled_name())
            players.append("Start game")

            players_menu = Menu("Players", players)
            players_menu.time_limit = 3
            players_menu.get_input()

            if players_menu.user_input == "Start game":
                if len(self.users) > 1:
                    break
                else:
                    error("You need at least 2 players to start a game!")

        # Wait loop has broken so therefore the game has started
        self.game_started = True

        # Removed any unconnected users
        for user in self.users:
            if not user.is_connected:
                self.users.remove(user)

        # Sync the game
        self.backend.sync_game()

        # Send the start game message after syncing
        time.sleep(0.5)
        self.backend.send_message_to_all("synced so start game", "move_on")

        if self.check_server_error(): return

        # Start the game, check if the game has finished or play the game
        if self.check_game_finished():
            # If the game has finished then show the results
            self.game_end()
        else:
            self.play()

        if self.check_server_error(): return

        # Kill the server
        self.backend.kill()

    def join_game(self, ip, port):
        """
        Joins a game
        """
        # Create a socket
        try:
            self.backend = QuizGameClient(ip, port)
            self.backend.game = self
        except OSError:
            error("Could not create a socket. Please try again.")
            return

        # Thread the server
        self.server_thread = threading.Thread(target=self.backend.run)
        self.server_thread.start()

        # Set up the user
        self.set_users()
        self.current_user_playing_net_name = self.users[0].name
        self.prepare_save_data()

        # Setup States
        debug_message("Connected to server on " + ip + ":" + str(port) + "!", "game_server")
        self.joined_game = True
        self.backend.running = True

        self.backend.send_message(self.backend.client, self.save_data["users"][0], "client_join")

        # Wait for send and response
        time.sleep(1)

        if self.check_server_error(): return

        # Wait for the server to start the game
        os.system("cls")
        print(f"Connected to server on {ip}:{port}! (Press Ctrl+C to quit)")
        print("Waiting for server to start the game...")

        # Wait for the server to start the game or socket to close
        self.backend.wait_for_move_on()

        # Play the game
        if self.check_server_error(): return
        self.play()
        if self.check_server_error(): return

        # Close the socket
        self.backend.close_connection(self.backend.client)

    def check_server_error(self) -> bool:
        # If the socket has closed then return and print any errors
        if not self.backend.running:
            if self.backend.error is not None:
                os.system("cls")
                error(self.backend.error)
                input("Press enter to continue...")
            return True
        return False

# TODO: Fix user progress loading. handle client quitting, More error handling
