# - - - - - - - Imports - - - - - - -#
import sys
import os

from Maxs_Modules.files import SaveFile
from Maxs_Modules.tools import debug, error
from Maxs_Modules.renderer import Menu

#              Variables       #
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


def get_settings():
    usersettings = UserSettings()

    if usersettings.display_mode is None:
        gui_or_cli()

    if usersettings.network is None:
        online_or_offline()

    game_main_menu()


def main():
    main_menu = Menu("Welcome to QUIZ", ["Quit", "Continue"])
    main_menu.show()

    match main_menu.user_input:
        case "Quit":
            sys.exit()
        case "Continue":
            get_settings()

    print("Done")


if __name__ == "__main__":
    handle_args(sys.argv)
    main()
