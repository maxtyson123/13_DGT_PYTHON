# - - - - - - - Imports - - - - - - -#
import os
import threading
import time
import html
import random

from Maxs_Modules.files import SaveFile, load_questions_from_file, UserData
from Maxs_Modules.network import get_ip, QuizGameServer, QuizGameClient
from Maxs_Modules.tools import try_convert, set_if_none, get_user_input_of_type, string_bool, sort_multi_array
from Maxs_Modules.debug import debug_message, error
from Maxs_Modules.renderer import Menu, divider, Colour, print_text_on_same_line

# - - - - - - - Variables - - - - - - -#
data_folder = "UserData/Games/"
category_offset = 9
max_number_of_questions = 50
quiz_categories = ("General Knowledge", "Books", "Film", "Music", "Musicals & Theatres", "Television", "Video Games",
                   "Board Games", "Science & Nature", "Computers", "Mathematics", "Mythology", "Sports", "Geography",
                   "History", "Politics", "Art", "Celebrities", "Animals", "Vehicles", "Comics", "Gadgets",
                   "Japanese Anime & Manga", "Cartoon & Animations")
host_a_server_by_default = False


# - - - - - - - Functions - - - - - - -#


def generate_new_save_file():
    """
    Generates a new save file name by searching through the data folder for a name that is not already taken in the
    format of "Game_0.json" (where 0 is the number of the save file). If more than 1000 save files are found, then an
    exception is raised to prevent infinite looping as most likely something has gone wrong.

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
    question_type = None
    difficulty = None
    question = None
    correct_answer = None
    incorrect_answers = None

    def __init__(self) -> None:
        pass

    # Note uses the string representation of Question class as it has not been defined therfore cant use it in type the
    # hints
    def load(self, data: dict) -> "Question":
        """
        Takes a dictionary of data and loads it into the question object. The data is also html character unescaped
        when loaded

        @param data: The dict to load the data from. Needs to have the following keys: category, type, difficulty,
        question, correct_answer, incorrect_answers
        @return: The question object
        """
        self.category = data.get("category")
        self.question_type = data.get("type")
        self.difficulty = data.get("difficulty")
        self.question = html.unescape(data.get("question"))

        self.correct_answer = html.unescape(data.get("correct_answer"))
        self.incorrect_answers = data.get("incorrect_answers")

        # Unescape the incorrect answers
        for answer_index in range(len(self.incorrect_answers)):
            self.incorrect_answers[answer_index] = html.unescape(self.incorrect_answers[answer_index])

        return self


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
        """
        Loads the data from a dictionary into the user object, if the data is None, then the default value is used.

        @param data: A dictionary of data to load into the user object. May contain the following keys: name, colour,
        icon, points, correct, incorrect, streak, highest_streak, questions_missed, answers, times, has_answered
        """
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
        to display them. The stats are stored in the following variables: questions_answered, accuracy, average_time,
        average_time_correct, average_time_incorrect, average_time_missed
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
        Calculates and then prints the stats for the user.
        """

        # Calculate any stats that aren't just supplied by the game
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
        icon and colour are kept.
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
        """
        Loads the data from the dictionary into the bot using the function provided by the User class with the added
        variable of accuracy. The defaults are then loaded.

        @param data: The dictionary containing the data to load, should contain the same keys as the User.load()
        function with an added accuracy key
        """
        super().load(data)
        self.accuracy = data.get("accuracy")
        self.load_defaults()

    def load_defaults(self) -> None:
        """
        Loads the default values for the bot, the defaults are the same as the User class with the addition of an
        default accuracy of 0.5 (50%). Also sets the player_type to "Bot"
        """
        super().load_defaults()
        self.accuracy = set_if_none(self.accuracy, 0.5)
        self.player_type = "Bot"

    def show_stats(self) -> None:
        """
        Prints the collected stats variables to the console. The actual accuracy is printed and the expected accuracy
        is also printed.
        """
        # Ensure that calculations don't mess with accuracy
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
    game_loaded = False
    cancelled = False

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
        Creates a new game. If the quiz_save is not none, then load the quiz save because the user wants to continue a
        game otherwise generate a new save file. After the save file is loaded, the default settings are set and then
        converted into their relevant classes.

        @param quiz_save: The name of the save file to load, if none then a new save file will be generated. (Default:
        None)
        """
        # Call the super class and pass the save file name, this will automatically load the settings

        # If the quiz save is not none, then load the quiz save because the user wants to continue a game otherwise
        # generate a new save file
        if quiz_save is not None:
            super().__init__(data_folder + quiz_save)
            self.game_loaded = True
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
        Shows the user various menus related to settings, allowing them to change the settings. Starts with the main
        gameplay settings menu
        """
        self.settings_gameplay()

    def convert_to_object(self, dicts: list, object_type: object) -> None:
        """
        Converts the dicts list from a list of item to a list of object_type objects. It will only attempt convert
        the item if it is not already a object_type object, therefore this function can be called without knowing the
        state of each item in the list
        """
        # For each user in the list of users convert the dict to a User object using the load() function
        for x in range(len(dicts)):
            # Check if the user is already a User object
            if type(dicts[x]) is object_type:
                continue

            # Load
            new_object = object_type()
            new_object.load(dicts[x])
            dicts[x] = new_object

    def set_players(self) -> None:
        """
        Clears the list of users and bots, and then gets a colour and name for each user. The amount of users is set in
        the settings menu. After the users have been set the bots are then created. The amount of bots is set in the
        settings menu
        """
        # Clear the users and bots lists
        self.users = []
        self.bots = []

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
                user.colour += Colour.ITALIC

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
        self.convert_to_object(self.questions, Question)

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

        # Convert the type if it is not any
        if self.question_type != "Any":

            match self.question_type:
                case "Multiple Choice":
                    self.api_type = "multiple"
                case "True/False":
                    self.api_type = "boolean"

    # __ GAME FUNCTIONS __

    def begin(self) -> None:
        """
        Starts the game. It first gets the questions if there are none, then shuffles the questions if the user wants
        (only if the game is a new one as when continuing the game the questions should be in the same order). If the
        game is set to be hosted then a server is started up. Afterwards the game is checked to see if it is finished
        othewise it will continue to play from the current state
        """
        # If there are no questions then get them
        if len(self.questions) == 0:
            self.get_questions()

        # Shuffle the questions if the user wants to
        if self.randomise_questions and not self.game_loaded:
            random.shuffle(self.questions)

        if self.host_a_server:
            self.wait_for_players()
            return

        # Start the game, check if the game has finished or play the game
        if self.check_game_finished():
            # If the game has finished then show the results
            self.game_end()
        else:
            self.game_started = True
            self.play()

    def show_scores(self) -> None:
        """
        Shows the scores of all the players in a menu with the points beside them sorted from highest to lowest. If the
        user selects a player their individual stats are show i.e accuracy and time etc.
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
        # causes errors because they are not ints)
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
        Shows the answer each player submitted for the questions. It begins at current_question and then goes through each
        question after that, so when called best practice is to set current_question to 0. It will call itself in a
        loop until it reaches the end of the questions array
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

        # Note to self, because python is python with its syntax, the "_" is what default is
        match marking_menu.get_input():
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
        Marks the question and updates the user class based on the mark. The marking (Correct, Incorrect, Missed) is
        added on to the current valued stored in the user's, answers array therefore before calling the marking
        function set the string to be "" or "Missed_".

        @param user_input: The answer submitted by the player, this is what will be checked against the correct answer
        @param current_user: The user that answered the question, and where the points will be added to.
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
        Shows the user the question in a menu and gets the user to answer it, utilising the Menu class's time_limit
        to force the user to answer in the specified amount of time. Then it marks the question and calculates the
        score for the player. Afterwards it runs the next question. The start time and end time of this function is
        calculated and then stored for later use to work out the timings for the stats.
        """

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
        clear()

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
        Increases the current question by 1 and then checks if the game is over or not. If the game is over then it
        will run the game_end() function. If the game is not over then it show the scores if specified so in
        show_score_after_question_or_game and then will run the next question. If this is a network game then it will
        wait for all the players to answer or for the server to move on.
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
            loading_amount = 1
            while True:
                waiting = False
                users_waiting = []

                # Loop through the users until one is found that hasn't answered
                for user in self.users:
                    if user.has_answered is False:
                        waiting = True
                        users_waiting.append(user.name)

                if not waiting:
                    break
                else:
                    print_text_on_same_line(
                        "Waiting for: " + ", ".join(users_waiting) + " to answer" + "." * loading_amount)
                    loading_amount += 1
                    if loading_amount > 3:
                        loading_amount = 1
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
            # Check that the server hasn't closed
            if self.check_server_error(): return

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

        # Check that the server hasn't closed
        if is_client:
            if self.check_server_error(): return

        # Move onto the question
        self.play()

    def check_game_finished(self) -> bool:
        """
        Checks if the game has finished and then will update the game_finished state. If the game has finished but
        there are multiple players (locally) then it will reset the question counter and increase the current user
        playing and then call play()
        @return: True if the game has finished, False if not.
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
                # TODO: Setting game finished here seems weird, could cause a bug (i.e continue game after all
                #  players have had turn as caller gets this false), fix later
            else:
                self.game_finished = True
        else:
            self.game_finished = False

        return self.game_finished

    def game_end(self) -> None:
        """
        Shows a menu allowing for the final scores to be show or to compare the answers of the users.
        """
        # Save that the game has ended
        self.save()

        # Create the game end menu
        game_end_menu = Menu("Game Finished", ["Compare Scores", "Compare User Answers", "Finish"])

        # Check what the user selected
        match game_end_menu.get_input():
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
         data but all settings and questions will be kept. The questions will be reshuffled is specified so
        """

        # Reset the current question
        self.current_question = 0
        self.current_user_playing = 0
        self.game_finished = False

        # Reset the users and bots
        for user in self.users:
            user.reset()
        for bot in self.bots:
            bot.reset()

        # Shuffle the questions
        if self.randomise_questions:
            random.shuffle(self.questions)

        # Save the game
        self.save()

    def prepare_save_data(self) -> None:
        """
        Prepares the save data for the game by converting the classes to dicts and removing the socket and thread
        from the dictionary. Similar to convert_to_object() the state of each item is not needed to be the same as it
        is compared using isinstance().
        """
        # Create the save data for the UserSettings object
        self.save_data = self.__dict__.copy()

        # Convert the user class to a dict
        for user_index in range(len(self.users)):
            # Check if the user is not already a dict (have to use isinstance as if it is a dict then user_index won't
            # work)
            if isinstance(self.users[user_index], User):
                # Convert the user to a dict
                self.users[user_index] = self.users[user_index].__dict__

        # Convert the question class to a dict
        for question_index in range(len(self.questions)):
            # Check if the question is a class
            if type(self.questions[question_index]) == Question:
                self.save_data["questions"][question_index] = self.questions[question_index].__dict__

        # Convert the bots to a dict
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
        Saves the game data to the file. Calls the prepare_save_data() function so the game can be in any-state when
        the caller is calling this function. After it has been written to the file the data is converted back.
        """
        self.prepare_save_data()

        # Call the super class save function
        super().save()

        # Convert everything back
        self.convert_all_from_save_data()

    def convert_all_from_save_data(self) -> None:
        """
        Using the convert_to_object function the users, questions and bots are all attempted to be converted to their
        relative classes
        """
        self.convert_to_object(self.users, User)
        self.convert_to_object(self.questions, Question)
        self.convert_to_object(self.bots, Bot)

    # __ MENUS __

    def settings_local(self) -> None:
        """
        Shows a menu to configure the settings for a local hosted game
        """
        local_menu_options = ["How many players", "Next", "Back"]
        local_menu_values = [str(self.how_many_players), "Play Game", "Gameplay Settings"]
        single_player_menu = Menu("Game Settings: Local", [local_menu_options, local_menu_values], True)

        while True:

            match single_player_menu.get_input():
                case "How many players":
                    self.how_many_players = get_user_input_of_type(int, "How many players")
                case "Next":
                    self.set_players()
                    break
                case "Back":
                    self.settings_gameplay()
                    break

    def settings_networking(self) -> None:
        """
        Shows a menu to configure the networking settings for the game

        """
        networking_menu_options = ["Server Name", "Server Port", "Max Players", "Next", "Back"]
        networking_menu_values = [str(self.server_name), str(self.server_port), str(self.max_players),
                                  "Waiting for players", "Gameplay Settings"]

        networking_menu = Menu("Game Settings: Networking", [networking_menu_options, networking_menu_values], True)

        while True:

            match networking_menu.get_input():

                case "Server Name":
                    self.server_name = get_user_input_of_type(str, "Server Name")

                case "Server Port":
                    self.server_port = get_user_input_of_type(int, "Server Port")

                case "Max Players":
                    self.max_players = get_user_input_of_type(int, "Max Players")

                case "Next":
                    break

                case "Back":
                    self.settings_gameplay()
                    break

    def settings_gameplay(self) -> None:
        """
        Shows a menu to configure the gameplay settings for the game
        """

        # Menu options get updated so menu setup has to be in a loop
        while True:
            game_play_menu_options = ["Host a server", "Time limit", "Question Amount", "Category", "Difficulty",
                                      "Type", "Show score after Question/Game",
                                      "Show correct answer after Question/Game", "Points for correct answer",
                                      "Points for incorrect answer", "Points for no answer",
                                      "Points multiplier for a streak", "Compounding amount for a streak",
                                      "Randomise questions", "Randomise answer placement",
                                      "Pick random question when run out of time",
                                      "Bot difficulty", "Number of bots", "Next", "Back"]

            game_play_menu_values = [str(self.host_a_server), str(self.time_limit), str(self.question_amount),
                                     str(self.quiz_category), str(self.quiz_difficulty), str(self.question_type),
                                     str(self.show_score_after_question_or_game),
                                     str(self.show_correct_answer_after_question_or_game),
                                     str(self.points_for_correct_answer), str(self.points_for_incorrect_answer),
                                     str(self.points_for_no_answer),
                                     str(self.points_multiplier_for_a_streak),
                                     str(self.compounding_amount_for_a_streak),
                                     str(self.randomise_questions), str(self.randomise_answer_placement),
                                     str(self.pick_random_question),
                                     str(self.bot_difficulty), str(self.how_many_bots)]

            # Add the "Next" Value
            if self.host_a_server:
                game_play_menu_values.append("Networking Settings")
            elif not self.host_a_server:
                game_play_menu_values.append("Local Settings")

            # Add the "Back" Value
            game_play_menu_values.append("Main Menu")

            gameplay_menu = Menu("Game Settings: Gameplay", [game_play_menu_options, game_play_menu_values], True)

            match gameplay_menu.get_input():
                case "Host a server":
                    self.host_a_server = get_user_input_of_type(string_bool,
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
                    self.quiz_difficulty = get_user_input_of_type(str, "Difficulty (Easy, Medium, Hard)",
                                                                  ["Easy", "Medium", "Hard"])

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
                    self.compounding_amount_for_a_streak = get_user_input_of_type(int,
                                                                                  "Compounding amount for a streak")

                case "Randomise questions":
                    self.randomise_questions = get_user_input_of_type(string_bool, "Randomise questions ("
                                                                      + Colour.true_or_false_styled() + ")")

                case "Randomise answer placement":
                    self.randomise_answer_placement = get_user_input_of_type(string_bool,
                                                                             "Randomise answer placement ("
                                                                             + Colour.true_or_false_styled() + ")")

                case "Pick random question when run out of time":
                    self.pick_random_question = get_user_input_of_type(string_bool, "Pick random question (" +
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
                    break

                case "Back":
                    self.cancelled = True
                    break

    def wait_for_players(self):
        """
        Creates a new server and sets it to the backend of this class. If there are no players then the user is asked
        to set the host player, otherwise whatever player is at index 0 will be set to the host. A menu is then
        shown, showing all the players currently in the game, it refreshes itself every 3 seconds via manipulation
        of the time_limit in the Menu class. When the host decides to start the game any old unconnected users will
        be removed from the game and the game will start. The server will then sync the game data with the clients
        and play() will be called.
        """

        # Set up the host (if there isn't one already) (host is always the first user in the list)
        if len(self.users) == 0:
            self.set_players()
        self.users[0].is_host = True
        self.users[0].is_connected = True

        # Create a socket
        try:
            self.backend = QuizGameServer(get_ip(), self.server_port)
            self.backend.game = self
        except OSError:
            error("Could not create a server (most likely already running on ip/port). Please try again.")
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
            self.convert_to_object(self.users, User)

            # Loop through all the users
            for user in self.users:
                # Add them to the list
                players.append(user.styled_name())
            players.append("Start game")
            players.append("Back")

            players_menu = Menu("Players", players)
            players_menu.time_limit = 3


            match players_menu.get_input():
                case "Start game":
                    if len(self.users) > 1:
                        break
                    else:
                        error("You need at least 2 players to start a game!")

                case "Back":
                    # Kill the server
                    self.backend.kill()
                    return

        # Wait loop has broken so the game has started
        self.game_started = True
        self.users[0].is_connected = True

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
        Joins a game, by creating a socket and connecting to the server on the given ip and port. The game is then
        ran when the server is ready. May return prematurely if an error occurs.
        """
        # Create a socket
        try:
            print("Connecting to server...")
            self.backend = QuizGameClient(ip, port)
            self.backend.game = self
        except OSError:
            error("Could not connect (socket not created). Please try again.")
            return

        # Thread the server
        self.server_thread = threading.Thread(target=self.backend.run)
        self.server_thread.start()

        # Set up the user
        self.set_players()
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
        # Start the game, check if the game has finished or play the game
        if self.check_game_finished():
            # If the game has finished then show the results
            self.game_end()
        else:
            self.play()
        if self.check_server_error(): return

        # Close the socket
        self.backend.close_connection(self.backend.client)

    def check_server_error(self) -> bool:
        """
        Checks if the server has closed and if so then prints any errors and returns True. If the server is still
        running and has no errors then returns False.
        @return:
        """
        # If the socket has closed then return and print any errors
        if not self.backend.running:
            if self.backend.error is not None:
                os.system("cls")
                error(self.backend.error)
                input("Press enter to continue...")
                self.backend.error = None
            return True
        return False
