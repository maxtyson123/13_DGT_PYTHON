# - - - - - - - Imports - - - - - - -#


import os

from Maxs_Modules.tools import get_user_input_of_type

# - - - - - - - Variables - - - - - - -#


console_width = 100
divider_symbol = "#"
divider = divider_symbol * console_width

# - - - - - - - Functions - - - - - - -#


def text_in_divider(item_to_print: str, auto_truncate: bool = True) -> str:
    """
    Prints the text in the divider

    @param item_to_print: The text to print
    @param auto_truncate: If the text is longer than the console width then truncate it
    @return: The text in the divider
    """
    # If the text is longer than the console width then truncate it
    if len(Colour.clean_text(item_to_print)) > console_width and auto_truncate:
        # Truncate the text to fit the console width
        item_to_print = item_to_print[:console_width - 2]

    # The length of the text, minus console width, minus 2 for the border
    width_left = console_width - len(Colour.clean_text(item_to_print)) - 2
    return divider_symbol + item_to_print + " " * width_left + divider_symbol


def show_menu(menu_items: list) -> None:
    """
    Prints the menu items and their index. This is wrapped inbetween two dividers
    @param menu_items: The list of menu items to print
    """
    print(divider)

    # Loop through all the items in the menu
    for x in range(len(menu_items)):
        item_to_print = " [" + str(x) + "]" + " " + menu_items[x]
        print(text_in_divider(item_to_print))
    print(divider)


def show_menu_double(menu_items: list) -> None:
    """
    Prints the menu items and their index on the left. On the right it prints the item's value. This is wrapped
    inbetween two dividers. The item is automatically truncated if it is longer than half the console width,
    allowing space for the divider and the value. @param menu_items:
    """
    print(divider)

    # Loop through all the items in the menu
    for x in range(len(menu_items[0])):

        # Create the two items to print
        item_to_print_1 = " [" + str(x) + "]" + " " + menu_items[0][x]
        item_to_print_2 = "(" + menu_items[1][x] + ") "

        # Truncate the text if it is too long
        allowed_width = int(console_width / 2)

        if len(Colour.clean_text(item_to_print_1)) > allowed_width:
            item_to_print_1 = item_to_print_1[:allowed_width - 2]  # Truncate the text to fit half the console width

        if len(Colour.clean_text(item_to_print_2)) > allowed_width:
            item_to_print_2 = item_to_print_1[:allowed_width - 2]  # Truncate the text to fit half the console width

        # Spacing inbetween the two items (similar to how it is done in "text_in_divider" function)
        # The length of the text, minus console width, minus 2 for the border
        width_left = console_width - len(Colour.clean_text(item_to_print_1)) - len(Colour.clean_text(item_to_print_2)) - 2
        spacing = " " * width_left

        # Combine the two items
        final_item_to_print = divider_symbol + item_to_print_1 + spacing + item_to_print_2 + divider_symbol
        print(final_item_to_print)

    print(divider)


# - - - - - - - Classes - - - - - - -#


class Colour:
    """
    A class that stores the colour codes for the different colours. Note: from https://en.wikipedia.org/wiki/ANSI_escape_code
    """
    # Colours
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    GREY = "\033[90m"

    colours_list = [BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, GREY]
    colours_names_list = ["Black", "Red", "Green", "Yellow", "Blue", "Magenta", "Cyan", "White", "Grey"]

    # Styles
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    INVERT = "\033[7m"
    STRIKETHROUGH = "\033[9m"

    styles_list = [BOLD, DIM, ITALIC, UNDERLINE, BLINK, INVERT, STRIKETHROUGH]
    styles_names_list = ["Bold", "Dim", "Italic", "Underline", "Blink", "Invert", "Strikethrough"]

    # Reset
    RESET = "\033[0m"

    # THEME
    error = RED
    info = BLUE
    success = GREEN
    warning = YELLOW

    @staticmethod
    def text_with_colour(text: str, colour: str) -> str:
        """
        Returns the text with the colour code before and after it

        @param text: The text to colour
        @param colour: The colour code
        @return: The coloured text
        """
        return colour + text + Colour.RESET

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Removes the colour codes from the text, useful when doing len() operations on the text


        @param text: The text to remove the colour codes from
        @return: The text without the colour codes (copy of original string)
        """

        uncoloured_text = text

        # Loop through all the colours
        for colour in Colour.colours_list:
            uncoloured_text = uncoloured_text.replace(colour, "")

        # Loop through all the styles
        for style in Colour.styles_list:
            uncoloured_text = uncoloured_text.replace(style, "")

        # Remove the reset code
        uncoloured_text = uncoloured_text.replace(Colour.RESET, "")

        # Return the uncoloured text
        return uncoloured_text

    @staticmethod
    def true_or_false_styled() -> str:
        """
        Returns a coloured true or false string
        @return: "(green)True/(red)False"
        """

        return Colour.text_with_colour("True", Colour.success) + "/" + Colour.text_with_colour("False", Colour.error)


class Menu:
    # Note for future, the print should be changed to a render() function that allows for the menu to be rendered in
    # different ways (CLI, GUI)

    title = "None"
    items = []
    user_input = "undefined"
    clear_screen = True
    multi_dimensional = None

    def __init__(self, title: str, items: list, multi_dimensional: bool = False) -> None:
        """
        Creates a menu object

        @param title: The title of the menu
        @param items: The items in the menu
        @param multi_dimensional: If the menu items array is multi-dimensional (i.e. has a value for each item)
        """
        self.title = title
        self.items = items
        self.multi_dimensional = multi_dimensional

    def show(self) -> None:
        """
        Prints the menu to a clear screen and then gets the user input as an index of the menu items. Then stores the
        item in the user_input variable
        """
        if  self.clear_screen:
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

            input_items = self.items[0]
        else:
            input_items = self.items

        options = [*range(len(input_items))]

        # Get the user input and validate it
        user_input = get_user_input_of_type(int, "Choose an option (" + str(options[0]) + "-"
                                            + str(options[len(options) - 1]) + ")", options)

        # Store the input
        if self.multi_dimensional:
            self.user_input = self.items[0][int(user_input)]
        else:
            self.user_input = self.items[int(user_input)]