# - - - - - - - Imports - - - - - - -#


import os
from Maxs_Modules.tools import get_user_input_of_type, error

# - - - - - - - Variables - - - - - - -#


console_width = 60
divider_symbol = "#"
divider = divider_symbol * console_width

# - - - - - - - Functions - - - - - - -#


def text_in_divider(item_to_print, auto_truncate=True):

    # If the text is longer than the console width then truncate it
    if len(item_to_print) > console_width and auto_truncate:
        item_to_print = item_to_print[:console_width - 2]  # Truncate the text to fit the console width

    width_left = console_width - len(item_to_print) - 2  # The length of the text, minus console width, minus 2 for the border
    return divider_symbol + item_to_print + " " * width_left + divider_symbol


def show_menu(menu_items):
    print(divider)

    # Loop through all the items in the menu
    for x in range(len(menu_items)):
        item_to_print = " [" + str(x) + "]" + " " + menu_items[x]
        print(text_in_divider(item_to_print))
    print(divider)


def show_menu_double(menu_items):
    print(divider)

    # Loop through all the items in the menu
    for x in range(len(menu_items[0])):
        final_item_to_print = ""

        # Create the two items to print
        item_to_print_1 = " [" + str(x) + "]" + " " + menu_items[0][x]
        item_to_print_2 = "(" + menu_items[1][x] + ") "

        # Truncate the text if it is too long
        allowed_width = int(console_width / 2)

        if len(item_to_print_1) > allowed_width:
            item_to_print = item_to_print_1[:allowed_width - 2]  # Truncate the text to fit half the console width

        if len(item_to_print_2) > allowed_width:
            item_to_print = item_to_print_1[:allowed_width - 2]  # Truncate the text to fit half the console width

        # Spacing inbetween the two items (similar to how it is done in "text_in_divider()" function)
        width_left = console_width - len(item_to_print_1) - len(item_to_print_2) - 2  # The length of the text, minus console width, minus 2 for the border
        spacing = " " * width_left

        # Combine the two items
        final_item_to_print = divider_symbol + item_to_print_1 + spacing + item_to_print_2 + divider_symbol
        print(final_item_to_print)

    print(divider)

# - - - - - - - Classes - - - - - - -#


class Menu:
    # Note for future, the print should be changed to a render() function that allows for the menu to be rendered in
    # different ways (CLI, GUI)

    title = "None"
    items = []
    user_input = "undefined"
    multi_dimensional = None

    def __init__(self, title, items, multi_dimensional=False):
        self.title = title
        self.items = items
        self.multi_dimensional = multi_dimensional

    def show(self):

        # Clear the screen
        os.system("cls")

        # Print the menu
        print(divider)
        print(text_in_divider(" " + self.title))
        if self.multi_dimensional:
            show_menu_double(self.items)
        else:
            show_menu(self.items)

        # Calculate the possible options
        if self.multi_dimensional:
            options = [*range(len(self.items[0]))]
        else:
            options = [*range(len(self.items))]

        # Get the user input and validate it
        user_input = get_user_input_of_type(int, "Choose an option (" + str(options[0]) + "-" + str(options[len(options) - 1]) + ")")

        # Store the input
        if self.multi_dimensional:
            self.user_input = self.items[0][int(user_input)]
        else:
            self.user_input = self.items[int(user_input)]