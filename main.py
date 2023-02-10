# - - - - - - - Imports - - - - - - -#
import sys

from Maxs_Modules.tools import debug
from Maxs_Modules.renderer import Menu
from Maxs_Modules.game import get_saved_games, Game
from Maxs_Modules.setup import UserData

# - - - - - - - Variables - - - - - - -#
data_folder = "UserData/"


# - - - - - - - Functions - - - - - - -#

def handle_args(args: list) -> None:
    print("Quiz running with args:")
    for arg in args:
        print(arg)


# - - - - - - - Classes - - - - - - -#


# - - - - - - - MENUS - - - - - - -#

def continue_game() -> None:
    """
    Show the user the continue game menu
    """
    # Get all the saved files and create a menu
    saves = get_saved_games()
    saves.append("Back")

    continue_menu = Menu("Continue Game", saves)
    continue_menu.show()

    # If the user selected back then return
    if continue_menu.user_input == "Back":
        game_main_menu()

    # Load the game object
    quiz = Game(continue_menu.user_input)

    # Start the game
    quiz.begin()


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

    settings_options = ["Display Mode", "Network", "Back"]
    settings_values = [str(usersettings.display_mode), str(usersettings.network), "Main Menu"]

    settings_menu = Menu("Settings", [settings_options, settings_values], True)
    settings_menu.show()

    match settings_menu.user_input:
        case "Display Mode":
            settings()

        case "Network":
            settings()

        case "Back":
            game_main_menu()


def game_main_menu() -> None:
    """
    Show the user the main menu
    """
    game_menu = Menu("Game Menu", ["Continue Game", "New Game", "Settings", "Quit"])

    usersettings = UserData()
    if usersettings.network is not None:
        if usersettings.network:
            debug("Network is enabled", "network")
            game_menu.items.insert(2, "Join Game")
        else:
            debug("Network is disabled", "network")

    game_menu.show()

    match game_menu.user_input:
        case "Continue Game":
            continue_game()

        case "New Game":
            new_game()

        case "Join Game":
            join_game()

        case "Settings":
            settings()

        case "Quit":
            sys.exit()


def main() -> None:
    """
    The main function, initialise the program and show the main menu
    """
    # Set up the program
    setup = UserData()
    setup.init_script()

    # Show the main menu
    main_menu = Menu("Welcome to QUIZ", ["Quit", "Continue"])
    main_menu.show()

    match main_menu.user_input:
        case "Quit":
            sys.exit()
        case "Continue":
            game_main_menu()

    print("Done")


if __name__ == "__main__":
    handle_args(sys.argv)
    main()
