# - - - - - - - Imports - - - - - - -#
import os
import sys

from natsort import natsorted

from Maxs_Modules.debug import debug_message, init_debug, close_debug_session, handle_arg
from Maxs_Modules.files import UserData
from game import get_saved_games, Game
from Maxs_Modules.network import get_ip
from Maxs_Modules.renderer import Menu, clear, render_text, get_input, init_gui, gui_close
from Maxs_Modules.tools import string_bool, ip_address

# - - - - - - - Variables - - - - - - -#
DATA_FOLDER = "UserData/"


# - - - - - - - MENUS - - - - - - -#

def game_finished(game: Game) -> None:
    """
    Shows a menu that allows the user to play again or return to the main menu, if the game does not have the
    game_finished variable set to True, it will only return to the main menu without letting the user choosing an option
    . Play again resets the game and calls the game.begin() function, once the reset game is finished the input loop
    will run again (using the same game object). When returning to the main menu the game.save_file will be deleted if
    it exists

    @param game: The Game object to use.
    @return: None, the function will break the loop when the user selects an option that leaves the menu
    """

    # Create the game finished menu, set the default choice to Main Menu
    game_finished_menu = Menu("Game Finished", ("Play Again", "Main Menu"))
    game_finished_menu.user_input = "Main Menu"

    # Loop until the user selects an option that leaves this menu
    while True:

        # Only allow for playing again if the game was completed, otherwise just return to the main menu
        if game.game_finished:
            game_finished_menu.get_input()

        # Handle the input
        match game_finished_menu.user_input:

            case "Play Again":

                # Replay the game
                game.reset()
                game.begin()

            case "Main Menu":
                # Delete the game save if it exists
                if os.path.exists(game.save_file) and game.game_finished:
                    debug_message(f"Deleting save file: {game.save_file}", "game_finished")
                    os.remove(game.save_file)

                # Return to the main menu by breaking the loop
                break


def continue_game() -> None:
    """
    Shows a menu that allows the user to continue a game, It allows the user to select a game from the saved games,
    folder, if the user selects a previously joined multiplayer game it will delete the save file and join the game
    instead of continuing
    """

    # Get all the saved files and create a menu
    saves = get_saved_games()
    saves = natsorted(saves)

    # Add back to the menu
    saves.append("Back")

    # Show the menu, no need for a loop as this menu doesn't get repeated
    continue_menu = Menu("Continue Game", saves)
    continue_menu.get_input()

    # If the user selected back then return
    if continue_menu.user_input == "Back":
        return

    # Load the game object
    quiz = Game(continue_menu.user_input)

    # Check if this is previous multiplayer game
    if quiz.joined_game:
        # Delete this game save as continuing a multiplayer game is server side
        debug_message(f"Deleting {quiz.save_file}", "quiz_load_game")
        os.remove(quiz.save_file)

        # Get the user to join the server of the game
        join_game()
        return

    # Start the game
    quiz.begin()

    # Show the game finished menu
    game_finished(quiz)


def new_game() -> None:
    """
    Creates a new game object, runs the settings setup and then starts the game (if not cancelled during settings)
    """
    # Create a new game object
    quiz = Game()

    # Get the user to configure the game
    quiz.set_settings()

    # Check if the user has cancelled the game, otherwise start the game
    if not quiz.cancelled:
        quiz.begin()

    # Show the game finished menu
    game_finished(quiz)


def join_game() -> None:
    """
    Shows the user a menu to join a game, the user can enter the ip and port of the server to join. The default values
    are the local ip and port 1234 as that is the default port for the server.
    """
    # Set the default server values, this makes it easier for joining a local game
    ip = get_ip()
    port = 1234

    # Show the join game menu
    join_menu_options = ["IP", "Port", "Join Game", "Back"]
    join_menu_values = [str(ip), str(port), "Join Game", "Main Menu"]
    join_menu = Menu("Join Game", [join_menu_options, join_menu_values], True)

    while True:
        # Make sure that if the values were updated that they are still in string form for the menu
        join_menu_values[0] = str(ip)
        join_menu_values[1] = str(port)

        # Get the user to input the ip and port
        match join_menu.get_input():
            case "IP":
                ip = join_menu.get_input_option(ip_address, "Please enter the IP: ")

            case "Port":
                port = join_menu.get_input_option(int, "Please enter the port: (1-65535)", range(1, 65535))

            case "Join Game":
                # Create a new game object and join the game
                quiz = Game()
                quiz.join_game(ip, port)

            case "Back":
                break


def settings() -> None:
    """
    Show the user a menu that allows them to change their already specified settings
    """

    # Loop this menu until the user selects an option that leaves this menu (Loop has to be before menu creation as it
    # gets updated)
    while True:

        # Get the current settings
        usersettings = UserData()

        # Create the settings menu, using the current settings as the values displayed
        settings_options = ("Display Mode", "Network", "Fix API", "Back")
        settings_values = (str(usersettings.display_mode), str(usersettings.network), str(usersettings.auto_fix_api),
                           "Main Menu")
        settings_menu = Menu("Settings", [settings_options, settings_values], True)

        # Show and get input from the menu
        match settings_menu.get_input():
            case "Display Mode":
                usersettings.display_mode = settings_menu.get_input_option(str, "How should the game be rendered? "
                                                                                "(CLI/GUI)", ["CLI", "GUI"])

            case "Network":
                usersettings.network = settings_menu.get_input_option(string_bool,
                                                                      "Do you want to use the network? (True/False)")

            case "Fix API":
                render_text("Note: Fixing the API involves removing parameters from the API call until it goes though, "
                            "this can fix errors where there arent enough questions of that type in the database, "
                            "however it can mean that the question types arent the same as the ones you selected.")

                usersettings.auto_fix_api = settings_menu.get_input_option(string_bool,
                                                                           "Do you want to auto fix the API if an "
                                                                           "error occurs? (True / False): ")

            case "Back":
                break

        # Save the modified settings
        usersettings.save()


def game_main_menu() -> None:
    """
    Show the user the main menu, allowing them to continue a game, start a new game, join a game, view the tutorial or
    quit
    """

    # Create the main menu
    game_menu = Menu("Game Menu", ["Continue Game", "New Game", "Tutorial", "Settings", "Quit"])

    # If the user is not connected to the network then don't add the join game option
    usersettings = UserData()

    if usersettings.network:
        debug_message("Network is enabled", "network")
        game_menu.items.insert(2, "Join Game")
    else:
        debug_message("Network is disabled", "network")

    # Loop this menu until the user selects an option that leaves this menu
    while True:

        # Show and get input from the menu
        match game_menu.get_input():
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
                break


def tutorial() -> None:
    """
    Show the user a tutorial on how to use the menus, host a game and join a game
    """
    # Intro
    render_text("- Welcome to the tutorial!")
    render_text("- This tutorial will show you how to play the game and how to use the menus")
    render_text("- To continue press enter")
    get_input()
    clear()

    # Game Settings Menu
    render_text("- The first menu you will see when creating a game is the game settings menu, this menu allows you to "
                "configure the game.")
    render_text(
        "- The current value of each setting is shown in brackets, to change the value of a setting choose the setting "
        "and then you will be promoted to enter a new value.")
    render_text("- To continue press enter")
    get_input()
    clear()
    render_text("- Here is an example of the game settings menu")
    render_text(
        "- Hint: When interacting with menus you can either use the index (number in square brackets) or the name of "
        "the option")
    tut_menu = Menu("Tutorial", [""])
    tut_menu.multi_dimensional = True
    tut_menu.items = (("Number of Questions", "Question Types", "Difficulty", "Time Limit"),
                      ("10", "All", "All", "No Time Limit"))
    tut_menu.get_input()
    render_text("-  You chose: " + tut_menu.user_input + ", here you would be able to change the value of the setting")
    render_text("-  To continue press enter")
    get_input()
    clear()

    # Play a game
    render_text("- Now that you know how to configure the game you can play a game")
    render_text(
        "- The game will display the question and then you will be prompted to enter your answer, you have until the "
        "time limit (default 10 seconds) to enter your answer and then if no answer is selected a option will be "
        "automatically selected (if configured so)")
    render_text(
        "- After that the game will show you the correct answer (if configured so) and then move on to the next "
        "question will be displayed or show the scores list depending on the game configuration")
    render_text("- When in the scores menu you can choose a player to see their stats")
    render_text("- To continue press enter")
    get_input()
    clear()

    # Network
    render_text("- The game also supports playing over a network, this allows you to play the game with your friends")
    render_text("- To play over a network you need to enable the network in the settings menu, if not already enabled")
    render_text(
        "- To play a networked game one player has to host a game by creating a game and then selecting the host a "
        "game setting and setting it to true. The other players then join the game by selecting the join game option "
        "and then pass the port and ip address of the host (displayed as option 0 on the host a game menu). Note: "
        "when playing over a network you may need to forward the port you are using to the computer you are using to"
        " be able to play the game over a non local network.")
    render_text(
        "- To continue a game the host can continue it like any other game, however the other players will need to "
        "use the same nicknames they used before to continue the game, additionally no new players can join the game.")
    render_text(
        "- When continuing a game that was part of a multiplayer game you will be sent to the join menu if you were "
        "not the host of the game.")
    render_text("- To continue press enter")
    get_input()
    clear()

    # End
    render_text("- That is the end of the tutorial, you can now play the game")
    render_text("- To continue press enter")
    get_input()
    clear()


def main() -> None:
    """
    The main function, initialise the program and show the main menu
    """
    # Get the pre-inputted user input
    user_input = handle_arg('--pass_input', True)
    render_text(user_input)

    # Show the main menu
    main_menu = Menu("Max's Quiz Game (13 DGT) (Open Trivia DB)", ("Quit", "Continue"))

    # Run the selected option
    match main_menu.get_input(user_input):
        case "Quit":
            sys.exit()
        case "Continue":
            game_main_menu()

    render_text("Thank you for playing Quiz Game by Max Tyson (13 DGT)")


def init_main() -> None:
    # Check if the desired folders exist and create them if they don't
    if not os.path.exists("UserData"):
        os.mkdir("UserData")

    if not os.path.exists("UserData/Games"):
        os.mkdir("UserData/Games")

    if not os.path.exists("ProgramData"):
        os.mkdir("ProgramData")

    if not os.path.exists("ProgramData/Logs"):
        os.mkdir("ProgramData/Logs")

    if not os.path.exists("ProgramData/Logs/Store"):
        os.mkdir("ProgramData/Logs/Store")


if __name__ == "__main__":
    # Set up the program
    init_debug()
    init_main()
    init_gui()

    # Run the main program and catch the exit to stop the debug session
    try:
        main()
    finally:
        close_debug_session()
        gui_close()
