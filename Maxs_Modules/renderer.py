# - - - - - - - Imports - - - - - - -#


import os

from Maxs_Modules.debug import debug, error
from Maxs_Modules.tools import get_user_input_of_type, try_convert

# - - - - - - - Variables - - - - - - -#


console_width = 100
divider_symbol = "#"
divider_symbol_size = len(divider_symbol)
divider = divider_symbol * console_width


# - - - - - - - Classes - - - - - - -#
class WrapMode:
    """
    A class that stores shorthands for the styling to preform when text is larger than the console width
    """
    NONE = 0
    CHAR = 1
    WORD = 2
    TRUNCATE = 2


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


class MenuManager:
    menu_history = []
    menu_input_history = []
    pre_input = []


menu_manager = MenuManager()


class Menu:
    # Note for future, the print should be changed to a render() function that allows for the menu to be rendered in
    # different ways (CLI, GUI)

    # Menu data
    title = "None"
    items = []
    user_input = "undefined"

    # Menu options
    clear_screen = True
    multi_dimensional = None
    wrap_mode = WrapMode.WORD

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
        menu_manager.menu_history.append(title)

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
        text_in_divider(" " + self.title, self.wrap_mode)
        if self.multi_dimensional:
            show_menu_double(self.items, self.wrap_mode)
        else:
            show_menu(self.items, self.wrap_mode)

        # Check if the menu has a pre-input
        if len(menu_manager.pre_input) > 0:

            # Check if the pre-input is a valid option index for this menu
            if menu_manager.pre_input[0] < len(self.items):
                # Store the input
                self.user_input = self.items[menu_manager.pre_input[0]]

                # Remove the pre-input
                menu_manager.pre_input.pop(0)

                # Add the input to the input history
                menu_manager.menu_input_history.append(self.user_input)

                # Return
                return

            else:
                # Print an error
                error("The pre-input (" + str(menu_manager.pre_input[0]) + ") was not a valid option for this menu")

                # Clear the pre-input
                menu_manager.pre_input = []


        # Calculate the possible options
        if self.multi_dimensional:

            input_items = self.items[0]
        else:
            input_items = self.items

        options = [*range(len(input_items))]

        # Get the user input and validate it, note cant use the get_user_input_of_type function as the menu also
        # allows for "pre-input" and choseing an item index or item itself
        user_input = ""

        while True:
            user_input = input("Choose an option (" + str(options[0]) + "-" + str(options[len(options) - 1]) + ") > ")

            # Check if the user is wanting to do pre-input (i.e a list of indexs "1,4,3,2")
            if "," in user_input:
                # Split the string into a list
                user_input = user_input.split(",")

                # Convert the list to ints
                user_input = [try_convert(item, int, True) for item in user_input]

                # Check if the list is valid
                if None not in user_input:
                    # Store the pre-input
                    menu_manager.pre_input = user_input

                    # Store the first input
                    self.user_input = self.items[menu_manager.pre_input[0]]

                    # Remove the first input from the pre-input
                    menu_manager.pre_input.pop(0)

                    # Add the input to the input history
                    menu_manager.menu_input_history.append(self.user_input)

                    # Return
                    return

                else:
                    error("Invalid pre-input, please enter a list of numbers separated by commas")
                    continue

            # Check if the user inputted an allowed string
            if user_input in input_items:
                self.user_input = user_input
                break

            user_input = try_convert(user_input, int)

            # If there is a type error then its returned as None otherwise it is the converted value
            if user_input is not None:
                    if user_input in options:
                        if self.multi_dimensional:
                            self.user_input = self.items[0][user_input]
                        else:
                            self.user_input = self.items[user_input]
                        break
                    else:
                        error("Invalid input, please enter one of these: " + str(options))


        menu_manager.menu_input_history.append(self.user_input)

# - - - - - - - Functions - - - - - - -#


def text_in_divider(item_to_print: str, wrap: WrapMode = WrapMode.TRUNCATE) -> None:
    """
    Prints the text in the divider

    @param item_to_print: The text to print
    @param wrap: How the text should be wrapped if it is too long (Truncate by default)
    @return: The text in the divider
    """
    text_length = len(Colour.clean_text(item_to_print))
    console_space_free = console_width - (divider_symbol_size * 2)

    # If the text is longer than the console width then wrap it
    if text_length > console_space_free:
        match wrap:
            case WrapMode.CHAR:
                # Print the current text in the divider, cutting off the text at the console width
                print(divider_symbol + item_to_print[:console_space_free] + divider_symbol)

                # Store the text to print as adding a space for readability
                item_to_print = " " + item_to_print[console_space_free:]

                # Re-run the function as many times as needed and then return so the original, un wrapped, text isn't
                # printed
                text_in_divider(item_to_print, wrap)
                return

            case WrapMode.WORD:
                # Split the text into words
                words = item_to_print.split(" ")

                # Store the current size
                current_size = 0

                item_to_print = ""

                # Loop through all the words
                for word in words:
                    # If this word is bigger then the entire console then split it up
                    if len(word) > console_space_free:
                        # Join the words together
                        item_to_print = " ".join(words)

                        # Print the item in the divider, split at console width
                        print(divider_symbol + item_to_print[:console_space_free] + divider_symbol)
                        current_size += console_space_free

                        # Store the text to print as adding a space for readability. Cut off the text already written
                        # and ignore the padding space
                        item_to_print = " " + item_to_print[current_size:]

                        # Re-run the function as many times as needed and then return so the original, un wrapped,
                        # text isn't printed
                        text_in_divider(item_to_print, wrap)
                        return

                    # If the current size plus the word length is less than the console width
                    if current_size + len(word) < console_space_free:
                        # Add the word to the current size
                        current_size += len(word)

                        # Add a space to the current size
                        current_size += 1

                        # Add the word to the text to print
                        item_to_print += word + " "

                    else:
                        # When here is reached then it is time to break out of the loop as the next word cant fit in
                        # the space left for this line

                        # Add spacing so the whole line is used
                        item_to_print += " " * (console_space_free - current_size)

                        # Break out of the loop
                        break

                # Print the item in the divider
                print(divider_symbol + item_to_print + divider_symbol)

                # Join the words together
                item_to_print = " ".join(words)

                # Store the text to print as adding a space for readability. Cut off the text already written and
                # ignore the padding space
                item_to_print = " " + item_to_print[current_size:]

                # Re-run the function as many times as needed and then return so the original, un wrapped, text isn't
                # printed
                text_in_divider(item_to_print, wrap)
                return

            case WrapMode.TRUNCATE:
                # Slice the text at console width - 2 (for the border)
                item_to_print = item_to_print[:console_space_free]

            case WrapMode.NONE:
                pass

    # The length of the text, minus console width, minus 2 for the border
    width_left = console_space_free - text_length
    print(divider_symbol + item_to_print + " " * width_left + divider_symbol)


def show_menu(menu_items: list, wrap: WrapMode = WrapMode.TRUNCATE) -> None:
    """
    Prints the menu items and their index. This is wrapped inbetween two dividers
    @param wrap: How the text should be wrapped if it is too long (Truncate by default)
    @param menu_items: The list of menu items to print
    """
    print(divider)

    # Loop through all the items in the menu
    for x in range(len(menu_items)):
        item_to_print = " [" + str(x) + "]" + " " + menu_items[x]
        text_in_divider(item_to_print, wrap)
    print(divider)


def show_menu_double(menu_items: list, wrap: WrapMode = WrapMode.TRUNCATE) -> None:
    """
    Prints the menu items and their index on the left. On the right it prints the item's value. This is wrapped
    inbetween two dividers. The item is automatically truncated if it is longer than half the console width,
    allowing space for the divider and the value.

    @param wrap: How the text should be wrapped if it is too long (Truncate by default)
    @param menu_items: The list of menu items to print
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

