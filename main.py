# TODOS:
# [x] Base functionality: menus etc, file saving/loading
# [x] Modules
# [x] Base Game Setup: Settings, questions from API/Local, etc
# [x] Clean Up
# [x] Extended user experience: Colours, mulitpage menus
# [x] Easier debugging
# [ ] Multiplayer Base: Joining a game, creating a game, waiting for players
# [ ] Multiplayer Game Logic: Scores sync questions sync
# [ ] Multiplayer Extended: Chat, etc
# [ ] Clean Up
# [ ] GUI Base, port the current render to a simple GUI
# [ ] GUI Extended, Buttons instead of based, css and other styling
# [ ] Clean Up
# [ ] Move the GUI and Multiplayer into mods and potentially make a mod API

# - - - - - - - Imports - - - - - - -#
import sys

from Maxs_Modules.renderer import Menu, Colour
from Maxs_Modules.debug import debug_message, init_debug, close_debug_session
from Maxs_Modules.game import get_saved_games, Game
from Maxs_Modules.setup import UserData
from Maxs_Modules.tools import get_user_input_of_type, strBool

# - - - - - - - Variables - - - - - - -#
data_folder = "UserData/"


# - - - - - - - Functions - - - - - - -#

def handle_args(args: list) -> None:
    print("Quiz running with args:")
    for arg in args:
        print(arg)


# - - - - - - - Classes - - - - - - -#


# - - - - - - - MENUS - - - - - - -#

def game_finished(game: Game) -> None:
    """
    Once the game is finished ask the user if they want to play again or quit

    @param game: The game object, used for resetting the game when replaying
    """
    game_finished_menu = Menu("Game Finished", ["Play Again", "Main Menu", "Quit"])
    game_finished_menu.get_input()

    match game_finished_menu.user_input:
        case "Play Again":

            # Replay the game
            game.reset()
            game.begin()

            # Show the game finished menu again
            game_finished(game)

        case "Main Menu":
            game_main_menu()

        case "Quit":
            sys.exit()


def continue_game() -> None:
    """
    Show the user the continue game menu
    """
    # Get all the saved files and create a menu
    saves = get_saved_games()
    saves.append("Back")

    continue_menu = Menu("Continue Game", saves)
    continue_menu.get_input()

    # If the user selected back then return
    if continue_menu.user_input == "Back":
        game_main_menu()

    # Load the game object
    quiz = Game(continue_menu.user_input)

    # Start the game
    quiz.begin()

    # Show the game finished menu
    game_finished(quiz)


def new_game() -> None:
    """
    Show the user a menu to create a new game
    """
    # Create a new game object
    quiz = Game()

    # Get the user to configure the game
    quiz.set_settings()

    # Save the game object
    quiz.save()

    # Start the game
    quiz.begin()

    # Show the game finished menu
    game_finished(quiz)


def join_game() -> None:
    """
    Show the user a menu to join a game
    """
    print("Join Game")
    # Show the user the join menu
    # Connect to server and wait for game to start


def settings() -> None:
    """
    Show the user a menu that allows them to change their already specified settings
    """
    usersettings = UserData()

    settings_options = ["Display Mode", "Network", "Fix API", "Python EXE Command", "Back"]
    settings_values = [str(usersettings.display_mode), str(usersettings.network), str(usersettings.auto_fix_api),
                       str(usersettings.python_exe_command), "Main Menu"]

    settings_menu = Menu("Settings", [settings_options, settings_values], True)
    settings_menu.get_input()

    match settings_menu.user_input:
        case "Display Mode":
            usersettings.display_mode = get_user_input_of_type(str, "Please enter the display mode (CLI, GUI): ",
                                                               ["CLI", "GUI"])

        case "Network":
            usersettings.network = get_user_input_of_type(strBool,
                                                          "Do you want to use the network? (" +
                                                          Colour.true_or_false_styled() + "): ")

        case "Fix API":
            print("Note: Fixing the API involves removing parameters from the API call until it goes though, "
                  "this can fix errors where there arent enough questions of that type in the database, however it "
                  "can mean that the question types arent the same as the ones you selected.")

            usersettings.auto_fix_api = get_user_input_of_type(strBool, "Do you want to auto fix the API if an error "
                                                                        "occurs? (" + Colour.true_or_false_styled() +
                                                               "): ")

        case "Python EXE Command":
            usersettings.python_exe_command = get_user_input_of_type(str, "Please enter the python executable command "
                                                                          "(e.g. python, python3, py): ")

        case "Back":
            game_main_menu()

    # Save and replay the menu if not going back
    if settings_menu.user_input != "Back":
        usersettings.save()
        settings()


def game_main_menu() -> None:
    """
    Show the user the main menu
    """
    game_menu = Menu("Game Menu", ["Continue Game", "New Game", "Tutorial", "Settings", "Quit"])

    usersettings = UserData()
    if usersettings.network is not None:
        if usersettings.network:
            debug_message("Network is enabled", "network")
            game_menu.items.insert(2, "Join Game")
        else:
            debug_message("Network is disabled", "network")

    game_menu.get_input()

    match game_menu.user_input:
        case "Continue Game":
            continue_game()

        case "New Game":
            new_game()

        case "Join Game":
            join_game()

        case "Tutorial":
            tutorial()

        case "Settings":
            settings()

        case "Quit":
            sys.exit()


def tutorial() -> None:
    tut_menu = Menu("Tutorial", [""])

    # Intro
    print("- Welcome to the tutorial!")
    print("- This tutorial will show you how to play the game and how to use the menus")
    print("- To continue press enter")
    input()
    tut_menu.clear()

    # Game Settings Menu
    print("- The first menu you will see when creating a game is the game settings menu, this menu allows you to "
          "configure the game.")
    print("- The current value of each setting is shown in brackets, to change the value of a setting choose the setting "
          "and then you will be promted to enter a new value.")
    print("- To continue press enter")
    input()
    tut_menu.clear()
    print("- Here is an example of the game settings menu")
    print("- Hint: When interacting with menus you can either use the index (number in square brackets) or the name of "
          "the option")
    tut_menu.multi_dimensional = True
    tut_menu.items = [["Number of Questions", "Question Types", "Difficulty", "Time Limit", "..."],
                      ["10", "All", "All", "No Time Limit", "..."]]
    tut_menu.get_input()
    print("-  You chose: " + tut_menu.user_input + ", here you would be able to change the value of the setting")
    print("-  To continue press enter")
    input()
    tut_menu.clear()

    # Play a game
    print("- Now that you know how to configure the game you can play a game")
    print("- The game will display the question and then you will be prompted to enter your answer, you have until the "
          "time limit (default 10 seconds) to enter your answer and then if no answer is selected a option will be "
          "automatically selected (if configured so)")
    print("- After that the game will show you the correct answer (if configured so) and then move on to the next "
          "question will be displayed or show the scores list depending on the game configuration")
    print("- When in the scores menu you can choose a player to see their stats")
    print("- To continue press enter")
    input()
    tut_menu.clear()

    # Network
    print(" No MULTIPLAYER YET so press enter to continue")
    input()
    tut_menu.clear()

    # End
    print("- That is the end of the tutorial, you can now play the game")
    print("- To continue press enter")
    input()
    tut_menu.clear()
    game_main_menu()


def main() -> None:
    """
    The main function, initialise the program and show the main menu
    """

    # Show the main menu
    main_menu = Menu("Max's Quiz Game (13 DGT) (Open Trivia DB)", ["Quit", "Continue"])
    main_menu.get_input()

    match main_menu.user_input:
        case "Quit":
            sys.exit()
        case "Continue":
            game_main_menu()

    print("Done")


if __name__ == "__main__":
    handle_args(sys.argv)

    # Set up the program
    setup = UserData()
    setup.init_script()
    init_debug()

    # Run the main program and catch the exit to stop the debug session
    try:
        main()
    finally:
        close_debug_session()
