# Spec: (JUMP TO LINE 60 TO SKIP)
#  - This module contains the Game class, which is the main class for the game.
#  - When playing in single player mode person A goes through the whole quiz then person B goes through the whole quiz.
#  - When playing in multiplayer mode person A and B go through the quiz simultaneously.
# External Functions:
#  - Join Game : Connects to a server and joins a game.
#  - Play Game : Starts a game.
#
# Internal Functions:
#  == (Main Gameplay functions) ==
#  [x] Start : Starts the game.
#  [ ] Quit : Quits the game.
#  [ ] Restart : Restarts the game.
#  [ ] Pause : Pauses the game.
#  [ ] Unpause : Unpauses the game.
#  [x] Save : Saves the game to a file.
#  [x] Load : Loads the game from a file.
#  [x] Set Settings : Sets the settings for the game.
#  [x] Set Users : Sets the users for the game. (Single player mode only)
#  [x] Get Questions : Gets the questions from the server (API).
#  == (Networking functions) ==
#  [ ] Connect : Connects to a server.
#  [ ] Disconnect : Disconnects from a server.
#  [ ] Send : Sends data to a server.
#  [ ] Receive : Receives data from a server.
#  [ ] Sync : Syncs the game with the server.
#  [ ] Host : Hosts a server.
#  [x] Get Quiz Data : Gets the quiz data from the server (API).
#  == (Gameplay functions) ==
#  [x] Display Options : Displays the options for the question.
#  [x] Mark Answer : Marks the answer as correct or incorrect.
#  [x] Get Input : Gets the user input.
#  [ ] Display Score : Displays the score of each player.
#  [ ] Bot Answer : Makes the bot answer the question.
#
# Settings:
#  == (Gameplay Settings) ==
#  [x] Game Mode : The game mode (Local Players or Multiplayer).
#  [x] Time Limit : The time limit for each question.
#  [ ] Show Score after Question or Game : Whether to show the score after each question or after the game
#      (This means that if it is shown after each question in single player, a snapshot of each player's score at that
#      question is needed).
#  [ ] Show Correct Answer after Question or Game : Whether to show the correct answer after each question or after the
#      game.
#  [x] Points for Correct Answer : The points for a correct answer.
#  [x] Points for Incorrect Answer : The points for an incorrect answer.
#  [x] Points for No Answer : The points for no answer.
#  [x] Points multiplier for a streak : The points multiplier for a streak.
#  [x] Compounding amount for a streak : The compounding amount for a streak.
#  [x] Randomise Questions : Whether to randomise the questions or not.
#  [x] Randomise Answers : Whether to randomise the answers placement or not.
#  [x] Pick Random Question : Whether to pick a random question or not once the time limit has been reached.
#  [ ] Bot Difficulty : The difficulty of the bot (% chance of picking the right answer out of 100).
#  == (Network Settings) ==
#  [ ] Server Name : The name of the server.
#  [ ] Server Port : The port of the server (1234 by default).
#  [ ] Max Players : The maximum amount of players.
#  == (Single Player Settings) ==
#  [x] How many players : The amount of players.
#  [ ] How many bots : The amount of bots.
#  == (Quiz Settings) ==
#  [x] Quiz Category : The category of the quiz.
#  [x] Quiz Difficulty : The difficulty of the quiz.
#  [x] Question Amount : The amount of questions.
#  [x] Question Type : The type of questions (True/False, Multi choice).
#  == (Player Settings) ==
#  [x] Player Name : The name of the player.
#  [ ] Player Colour : The colour of the player.
#  [ ] Player Icon : The icon of the player (GUI Only).

# - - - - - - - Imports - - - - - - -#
import os
import threading
import time
import html
import random

from Maxs_Modules.files import SaveFile, load_questions_from_file
from Maxs_Modules.setup import UserData
from Maxs_Modules.tools import debug, try_convert, set_if_none, get_user_input_of_type, strBool
from Maxs_Modules.renderer import Menu, divider

# - - - - - - - Variables - - - - - - -#
data_folder = "UserData/Games/"
category_offset = 9
max_number_of_questions = 50
quiz_categories = ["General Knowledge", "Books", "Film", "Music", "Musicals & Theatres", "Television", "Video Games",
                   "Board Games", "Science & Nature", "Computers", "Mathematics", "Mythology", "Sports", "Geography",
                   "History", "Politics", "Art", "Celebrities", "Animals", "Vehicles", "Comics", "Gadgets",
                   "Japanese Anime & Manga", "Cartoon & Animations"]


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
    incorrect = 0
    streak = 0
    questions_missed = 0

    def __int__(self, name: str, colour: str, icon: str) -> object:
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
        self.name = data.get("name")
        self.colour = data.get("colour")
        self.icon = data.get("icon")
        self.points = data.get("points")
        self.correct = data.get("correct")
        self.incorrect = data.get("incorrect")
        self.streak = data.get("streak")
        self.questions_missed = data.get("questions_missed")
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
        self.questions_missed = set_if_none(self.questions_missed, 0)


class Question:
    category = None
    type = None       # Although type is a reserved word, it is used in the API and is therefore used here
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
    online_enabled = None

    # API Conversion
    api_category = None
    api_type = None

    # Game data
    users = None
    questions = None

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

        # Load User Settings
        self.host_a_server = try_convert(self.save_data.get("host_a_server"), str)
        self.time_limit = try_convert(self.save_data.get("time_limit"), int)
        self.show_score_after_question_or_game = try_convert(self.save_data.get("show_score_after_question_or_game"),
                                                             str)
        self.show_correct_answer_after_question_or_game = try_convert(self.save_data.get("show_correct_answer_after_question_or_game"), str)
        self.points_for_correct_answer = try_convert(self.save_data.get("points_for_correct_answer"), int)
        self.points_for_incorrect_answer = try_convert(self.save_data.get("points_for_incorrect_answer"), int)
        self.points_for_no_answer = try_convert(self.save_data.get("points_for_no_answer"), int)
        self.points_multiplier_for_a_streak = try_convert(self.save_data.get("points_multiplier_for_a_streak"), int)
        self.points_multiplier_for_a_streak_base = try_convert(self.save_data.get("points_multiplier_for_a_streak_base"), int)
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

        # Load Game Data
        self.users = try_convert(self.save_data.get("users"), list)
        self.questions = try_convert(self.save_data.get("questions"), list)

        # Set the default settings if the settings are none
        self.set_settings_default()

        # Convert the data
        self.convert_users()
        self.convert_questions()

    def set_settings_default(self) -> None:
        """
        Sets the default settings if the settings are none
        """
        # User Chosen Settings
        self.host_a_server = set_if_none(self.host_a_server, False)
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

        # Game Data
        self.users = set_if_none(self.users, [])
        self.questions = set_if_none(self.questions, [])

    def set_settings(self) -> None:
        """
        Shows the user various menus related to settings, allowing them to change the settings
        """
        self.settings_how_to()

    def convert_users(self) -> None:
        """
        Converts the users list from a list of dicts to a list of User objects
        
        @return: This function returns if the list is empty or if the first item is already a User object
        """
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

    def set_users(self) -> None:
        """
        Gets the user to enter the names and colours for each user
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
            colour_menu = Menu("Choose a colour for " + user.name, ["Red", "Green", "Blue", "Yellow", "Purple",
                                                                    "Orange", "Pink", "Black", "White"])
            colour_menu.show()
            user.colour = colour_menu.user_input

            # Add to list of users
            self.users.append(user)

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

        debug("Questions: " + str(self.questions), "Game")

        # Convert the data into a list of Question objects
        self.convert_questions()

        # Shuffle the questions if the user wants to
        if self.randomise_questions:
            random.shuffle(self.questions)

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
                case "True or False":
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

    def begin(self) -> None:
        """
        Starts the game by printing all the users and then getting the questions if there are none
        """
        for user in self.users:
            print(user.name)

        # If there are no questions then get them
        if len(self.questions) == 0:
            self.get_questions()

        # Start the game, using the next_question function as this checks for the end of the game
        self.next_question()

    def mark_question(self, user_input) -> None:
        # Get the current question
        current_question = self.questions[self.current_question]

        # Get the current user
        current_user = self.users[self.current_user_playing]

        # Check if the answer is correct
        if user_input == current_question.correct_answer:
            # Tell the user that the answer is correct
            print("Correct!")

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

            # Add correct
            current_user.correct += 1

        else:
            print("Incorrect.")

            # Reset the streak
            current_user.streak = 0
            self.points_multiplier_for_a_streak = self.points_multiplier_for_a_streak_base

            # Add incorrect
            current_user.incorrect += 1

            # If the answer is not correct then remove a point from the user
            current_user.points -= self.points_for_incorrect_answer

    def play(self) -> None:
        """
        Shows the user the question and then gets the user to answer it in the specified time by using a different
        thread for the user input. Then it marks the question and calculates the score for the player. Afterwards it
        runs the next question
        """
        # Save the users progress
        self.save()

        # Get the current question
        current_question = self.questions[self.current_question]

        # Get the current user
        current_user = self.users[self.current_user_playing]

        # Create options
        options = current_question.incorrect_answers
        options.append(current_question.correct_answer)

        # Shuffle the options
        if self.randomise_answer_placement:
            random.shuffle(options)

        # Print some info
        print(divider)
        print("Question " + str(self.current_question + 1) + " of " + str(self.question_amount))
        print("User: " + current_user.name)
        print("Time Limit: " + str(self.time_limit) + " seconds")

        # Create the question menu
        question_menu = Menu(current_question.question, options)

        # Don't clear the screen as information is printed before the menu
        question_menu.dont_clear_screen()

        # Store the time and input
        time_limit = self.time_limit
        t = threading.Thread(target=question_menu.show)
        t.start()
        t.join(timeout=time_limit)

        if not t.is_alive():
            self.mark_question(question_menu.user_input)

        else:

            # If the game should pick a random question when the time runs out
            if self.pick_random_question:
                # Get a random option
                random_option = random.choice(options)
                print("Auto picking: "+random_option)
                self.mark_question(random_option)

            else:
                # Add the points for no answer
                current_user.points += self.points_for_no_answer

            # Add missed question to the user
            current_user.questions_missed += 1

            print("\nTime's up! Moving to next question.")

        # Give user time to read the answer
        time.sleep(1)

        # Move onto the next question
        self.next_question()

    def next_question(self) -> None:
        """
        Moves onto the next question. If the game has finished then it shows the results.
        """
        # Move onto the next question
        self.current_question += 1

        # Check if the game has finished
        if self.current_question == self.question_amount:

            # Check if it is another user's turn
            if self.current_user_playing < len(self.users) - 1:
                # If it is another user's turn then move onto the next user
                self.current_user_playing += 1
                self.current_question = 0

                # Move onto the next question
                self.play()

            # If the game has finished then show the results
            print("Game finished!")

        else:
            # Move onto the question
            self.play()

    def save(self) -> None:
        """
        Saves the game data to the file. Converts the user and question objects to dicts before saving and then
        converts them back once written to the JSON file
        """
        # Create the save data for the UserSettings object
        self.save_data = self.__dict__

        # Convert the user class to a dict
        for user_index in range(len(self.users)):
            self.save_data["users"][user_index] = self.users[user_index].__dict__

        # Convert the question class to a dict
        for question_index in range(len(self.questions)):
            self.save_data["questions"][question_index] = self.questions[question_index].__dict__

        # Call the super class save function
        super().save()

        # Convert the data back to the original format
        self.convert_users()
        self.convert_questions()

    def settings_questions(self) -> None:
        """
        Shows a menu to configure the questions for the game

        """
        questions_menu_options = ["Question Amount", "Category", "Difficulty", "Type", "Next"]
        questions_menu_values = [str(self.question_amount), self.quiz_category, self.quiz_difficulty,
                                 self.question_type]

        if not self.online_enabled:
            questions_menu_values.append("Set up players")
        else:
            questions_menu_values.append("Wait for players")

        questions_menu = Menu("Game Settings: Questions", [questions_menu_options, questions_menu_values], True)
        questions_menu.show()

        match questions_menu.user_input:
            case "Question Amount":
                self.question_amount = get_user_input_of_type(int, "Question Amount", range(1, 51))

            case "Category":
                category_menu = Menu("Category", quiz_categories)
                category_menu.show()
                self.quiz_category = category_menu.user_input

            case "Difficulty":
                self.quiz_difficulty = get_user_input_of_type(str, "Difficulty (Any, Easy, Medium, Hard)",
                                                              ["Any", "Easy", "Medium", "Hard"])

            case "Type":
                self.question_type = get_user_input_of_type(str, "Type (Any, Multiple, True/False)",
                                                            ["Any", "Multiple", "True/False"])

            case "Next":

                # Set up the users if the user is not hosting a server
                if not self.host_a_server:
                    self.set_users()

        # Loop if they chose to modify the settings, do not loop if they chose to go to next menu
        if questions_menu.user_input != "Next":
            self.settings_questions()

    def settings_local(self) -> None:
        """
        Shows a menu to configure the settings for a local hosted game
        """
        local_menu_options = ["How many players", "Next"]
        local_menu_values = [str(self.how_many_players), "Questions Settings"]
        single_player_menu = Menu("Game Settings: Local", [local_menu_options, local_menu_values], True)
        single_player_menu.show()

        match single_player_menu.user_input:
            case "How many players":
                self.how_many_players = get_user_input_of_type(int, "How many players")

            case "Next":
                self.settings_questions()

        # Loop if they chose to modify the settings, do not loop if they chose to go to next menu
        if single_player_menu.user_input != "Next":
            self.settings_local()

    def settings_networking(self) -> None:
        """
        Shows a menu to configure the networking settings for the game

        """
        networking_menu_options = ["Server Name", "Server Port", "Max Players", "Next"]
        networking_menu_values = [str(self.server_name), str(self.server_port), str(self.max_players),
                                  "Questions Settings"]

        networking_menu = Menu("Game Settings: Networking", [networking_menu_options, networking_menu_values], True)
        networking_menu.show()

        match networking_menu.user_input:

            case "Server Name":
                self.server_name = get_user_input_of_type(str, "Server Name")

            case "Server Port":
                self.server_port = get_user_input_of_type(int, "Server Port")

            case "Max Players":
                self.max_players = get_user_input_of_type(int, "Max Players")

            case "Next":
                self.settings_questions()

        # Loop if they chose to modify the settings, do not loop if they chose to go to next menu
        if networking_menu.user_input != "Next":
            self.settings_networking()

    def settings_gameplay(self) -> None:
        """
        Shows a menu to configure the gameplay settings for the game
        """
        game_play_menu_options = ["Host a server", "Time limit", "Show score after Question/Game",
                                  "Show correct answer after Question/Game",
                                  "Points for correct answer", "Points for incorrect answer",
                                  "Points for no answer", "Points multiplier for a streak",
                                  "Compounding amount for a streak", "Randomise questions",
                                  "Randomise answer placement",
                                  "Pick random question when run out of time",
                                  "Bot difficulty", "Number of bots", "Next"]

        game_play_menu_values = [str(self.host_a_server), str(self.time_limit),
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
        gameplay_menu.show()

        match gameplay_menu.user_input:
            case "Host a server":
                self.host_a_server = get_user_input_of_type(strBool, "Host a server (True/False)")

            case "Time limit":
                self.time_limit = get_user_input_of_type(int, "Time limit (seconds)")

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
                self.randomise_questions = get_user_input_of_type(strBool, "Randomise questions (True/False)")

            case "Randomise answer placement":
                self.randomise_answer_placement = get_user_input_of_type(strBool,
                                                                         "Randomise answer placement (True/False)")

            case "Pick random question when run out of time":
                self.pick_random_question = get_user_input_of_type(strBool, "Pick random question (True/False)")

            case "Bot difficulty":
                self.bot_difficulty = get_user_input_of_type(int, "Bot difficulty (1-10)", range(1, 11))

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

    def settings_how_to(self) -> None:
        """
        Shows a menu to explain how to use the game settings menu
        """
        os.system("cls")

        print("Game Settings: How To")
        time.sleep(1)

        print(
            "You will be shown menus relating to the game settings, you can change the settings by typing in the number"
            "of the option you want to change, otherwise the default will be used")

        input("Press enter to continue...")
        self.settings_gameplay()
