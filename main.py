################ Imports ################
import sys
import os
import time
import json

################ Variables ################
console_width = 30
divider_symbol = "#"
divider = divider_symbol * console_width


################ Functions ################

def handle_args(args):
    print("Quiz running with args:")
    for arg in args:
        print(arg)


def error(error_message):
    print(error_message)
    time.sleep(2)


def debug(debug_message, type="info"):
    print("[DEBUG] : " + debug_message)


def validate_user_input_number(input):
    try:
        int(input)  # trys to convert to int
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


################ Classes ################

class SaveFile:

    save_file = "settings.json"
    save_data = {}

    def __init__(self, save_file, auto_load=True):
        self.save_file = save_file

        # If the user wants to autoload the settings then try run the load function
        if auto_load:
            debug("Auto loading settings", "save_file")
            self.load()

    def load(self):
        debug("Loading file from " + self.save_file, "save_file")

        # Try to load the settings from the save file in read mode, if it fails then warn the user
        try:
            with open(self.save_file, "r") as file:
                debug("File opened", "save_file")

                # Try Load the data from the file and convert it to a dictionary, if it fails then warn the user and close the file then delete the file
                try:
                    self.save_data = json.load(file)
                except json.decoder.JSONDecodeError:
                    error("Settings file is corrupt, deleting file automatically")
                    file.close()
                    os.remove(self.save_file)
                    return

                # Set the variables to the saved data
                debug(str(self.save_data), "save_file")

                # Close the file
                file.close()

        except FileNotFoundError:
            error("Settings file not found")

    def save(self):
        debug("Saving file to " + self.save_file, "save_file")

        # Open the file and dump the UserSettings object as a dictionary, then close the file
        with open(self.save_file, "w") as file:
            save_dict = self.save_data

            # Try Remove the save_data dictionary from the save data as this causes an loop error when serializing
            try:
                del save_dict["save_data"]
            except KeyError:
                print("KeyError: save_data")

            debug("File data: " + str(save_dict), "save_file")

            json.dump(save_dict, file)
            file.close()


class UserSettings(SaveFile):

    display_mode = None
    network = None

    def __init__(self):

        # Call the super class and pass the save file name, this will automatically load the settings
        super().__init__("settings.json")

        # Set the variables to the saved data (using ".get()" to prevent errors if the data is not found)
        self.display_mode = self.save_data.get("display_mode")

    def save(self):

        # Create the save data for the UserSettings object
        self.save_data = self.__dict__

        # Call the super class save function
        super().save()


class Menu:

    # Note for future, the print should be changed to a render() function that allows for the menu to be rendered in different ways (CLI, GUI)

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


################ Menus ################

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
            game_menu.items.insert(2, "Join Game")

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
        debug(usersettings.network, "user_settings")

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
