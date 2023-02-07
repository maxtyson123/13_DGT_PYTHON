################ Imports ################
import sys
import os
import time
import json

################ Variables ################
console_width = 30
divider_symbol = "#"
divider = divider_symbol * console_width


################ Classes ################
class UserSettings:

    save_file = "settings.json"
    display_mode = None

    def __init__(self, save_file, auto_load=True):
        self.save_file = save_file

        # If the user wants to auto load the settings then try run the load function
        if auto_load:
            self.load()

    def load(self):
        # Try to load the settings from the save file in read mode, if it fails then warn the user
        try:
            with open(self.save_file, "r") as file:
                self.display_mode = file.read()
                file.close()
        except FileNotFoundError:
            error("Settings file not found")

    def save(self):

        # Open the file and dump the UserSettings object as a dictionary, then close the file
        with open(self.save_file, "w") as file:
            json.dump(self, file)
            file.close()


################ Functions ################

def handle_args(args):
    print("Quiz running with args:")
    for arg in args:
        print(arg)


def error(error_message):
    print(error_message)
    time.sleep(2)

def validate_user_input_number(input):
    try:
        int(input)  # trys to convert to int
        return True
    except ValueError:  # if it cant the return error
        error("Invalid input, please enter a number")
        return False


def menu(menu_title, menu_items):
    # Clear the screen
    os.system("cls")

    # Print the menu
    print(divider)
    text_in_divider(" " + menu_title)
    show_menu(menu_items)

    # Calculate the possible options
    options = [*range(len(menu_items))]

    # Get the user input and validate it
    invalid_input = True
    user_input = "null"
    while invalid_input:
        user_input = input("Choose an option (" + str(options[0]) + "-" + str(options[len(options) - 1]) + ") :")       # Get the user input
        if validate_user_input_number(user_input):                                                                      # Check if the user inputted a number
            if int(user_input) in options:                                                                              # Check if the user inputted a valid option
                invalid_input = False                                                                                   # If it is valid then stop the loop
            else:
                error("Invalid input, please enter a valid option")                                                     # If it is not valid then print error

    # Return the user input
    return menu_items[int(user_input)]


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


################ Menus ################

def gui_or_cli():
    menu_items = ["GUI", "CLI"]
    menu_title = "GUI or CLI?"
    user_input = menu(menu_title, menu_items)

    match user_input:
        case "GUI":
            print("GUI")
        case "CLI":
            print("CLI")


def main():
    main_menu_items = ["Quit", "Continue"]
    main_menu_title = "Welcome to QUIZ"
    user_input = menu(main_menu_title, main_menu_items)

    match user_input:
        case "Quit":
            sys.exit()
        case "Continue":
            gui_or_cli()


if __name__ == "__main__":
    handle_args(sys.argv)
    main()
