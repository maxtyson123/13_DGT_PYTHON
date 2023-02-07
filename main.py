# - - - - - - - Imports - - - - - - -#
import sys
import os

from Maxs_Modules.files import SaveFile
from Maxs_Modules.tools import debug, error

#              Variables       #
console_width = 30
divider_symbol = "#"
divider = divider_symbol * console_width
data_folder = "UserData/"


# - - - - - - - Functions - - - - - - -#

def try_convert(variable, type_to_convert):
    if variable is None:
        return None

    try:
        return type_to_convert(variable)
    except ValueError:
        error("Invalid input")
        return None


def handle_args(args):
    print("Quiz running with args:")
    for arg in args:
        print(arg)




def validate_user_input_number(user_input):
    try:
        int(user_input)  # try to convert to int
        return True
    except ValueError:  # if it cant the return error
        error("Invalid input, please enter a number")
        return False


def text_in_divider(item_to_print):
    width_left = console_width - len(
        item_to_print) - 2  # The length of the text, minus console width, minus 2 for the border
    print(divider_symbol + item_to_print + " " * width_left + divider_symbol)


def show_menu(menu_items):
    print(divider)

    # Loop through all the items in the menu
    for x in range(len(menu_items)):
        item_to_print = " [" + str(x) + "]" + " " + menu_items[x]
        text_in_divider(item_to_print)
    print(divider)


# - - - - - - - Classes - - - - - - -#


class UserSettings(SaveFile):
    display_mode = None
    network = None

    def __init__(self):
        # Call the super class and pass the save file name, this will automatically load the settings
        super().__init__(data_folder + "settings.json")

        # Set the variables to the saved data (using ".get()" to prevent errors if the data is not found)
        self.display_mode = try_convert(self.save_data.get("display_mode"), str)
        self.network = try_convert(self.save_data.get("network"), bool)

    def save(self):
        # Create the save data for the UserSettings object
        self.save_data = self.__dict__

        # Call the super class save function
        super().save()


class Menu:
    # Note for future, the print should be changed to a render() function that allows for the menu to be rendered in
    # different ways (CLI, GUI)

    title = "None"
    items = []
    user_input = "undefined"

    def __init__(self, title, items):
        self.title = title
        self.items = items

    def show(self):

        # Clear the screen
        os.system("cls")

        # Print the menu
        print(divider)
        text_in_divider(" " + self.title)
        show_menu(self.items)

        # Calculate the possible options
        options = [*range(len(self.items))]

        # Get the user input and validate it
        invalid_input = True
        user_input = "null"
        while invalid_input:
            user_input = input("Choose an option (" + str(options[0]) + "-" + str(
                options[len(options) - 1]) + ") :")  # Get the user input
            if validate_user_input_number(user_input):  # Check if the user inputted a number
                if int(user_input) in options:  # Check if the user inputted a valid option
                    invalid_input = False  # If it is valid then stop the loop
                else:
                    error("Invalid input, please enter a valid option")  # If it is not valid then print error

        # Store the input
        self.user_input = self.items[int(user_input)]


# - - - - - - - Functions - - - - - - -#

def continue_game():
    print("Continue Game")


def new_game():
    print("New Game")


def join_game():
    print("Join Game")


def settings_menu():
    print("Settings Menu")


def game_main_menu():
    game_menu = Menu("Game Menu", ["Continue Game", "New Game", "Settings", "Quit"])

    usersettings = UserSettings()
    if usersettings.network is not None:
        if usersettings.network:
            debug("Network is enabled", "network")
            game_menu.items.insert(2, "Join Game")
        else:
            print("Network is disabled")

    else:
        debug("Network is not set", "network")
        game_menu.items.insert(2, "Online or Offline")

    game_menu.show()

    match game_menu.user_input:
        case "Continue Game":
            continue_game()

        case "New Game":
            new_game()

        case "Join Game":
            join_game()

        case "Online or Offline":
            online_or_offline()

        case "Settings":
            settings_menu()

        case "Quit":
            sys.exit()


def online_or_offline():
    online_or_offline_menu = Menu("Online or Offline", ["Online", "Offline"])
    online_or_offline_menu.show()

    usersettings = UserSettings()

    if usersettings.network is not None:
        debug(str(usersettings.network), "user_settings")

    match online_or_offline_menu.user_input:
        case "Online":
            usersettings.network = True
        case "Offline":
            usersettings.network = False

    # Save the settings and move on
    usersettings.save()
    game_main_menu()


def gui_or_cli():
    gui_or_cli_menu = Menu("GUI or CLI", ["GUI", "CLI"])
    gui_or_cli_menu.show()

    usersettings = UserSettings()
    if usersettings.display_mode is not None:
        debug(usersettings.display_mode, "user_settings")

    match gui_or_cli_menu.user_input:
        case "GUI":
            usersettings.display_mode = "GUI"

        case "CLI":
            usersettings.display_mode = "CLI"

    # Save the settings and move on
    usersettings.save()
    online_or_offline()


def main():
    main_menu = Menu("Welcome to QUIZ", ["Quit", "Continue"])
    main_menu.show()

    match main_menu.user_input:
        case "Quit":
            sys.exit()
        case "Continue":
            gui_or_cli()

    print("Done")


if __name__ == "__main__":
    handle_args(sys.argv)
    main()
