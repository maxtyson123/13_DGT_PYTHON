# - - - - - - - Imports - - - - - - -#


import os
import sys
import threading
import time

from Maxs_Modules.debug import debug_message
from Maxs_Modules.files import UserData
from Maxs_Modules.tools import get_user_input_of_type, install_package

try:
    import eel
except ImportError:
    install_package("eel")
    import eel
# - - - - - - - Variables - - - - - - -#


console_width = 100
divider_symbol = "-"
divider_symbol_size = len(divider_symbol)
divider = divider_symbol * console_width
menu_manager = None
max_menu_items_per_page = 10
imported_timeout = False
display_type = UserData().display_mode


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
    A class that stores the colour codes for the different colours.
    Note: from https://en.wikipedia.org/wiki/ANSI_escape_code
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

    colours_list = (BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, GREY)
    colours_names_list = ("Black", "Red", "Green", "Yellow", "Blue", "Magenta", "Cyan", "White", "Grey")

    # Styles
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    INVERT = "\033[7m"
    STRIKETHROUGH = "\033[9m"

    styles_list = (BOLD, DIM, ITALIC, UNDERLINE, BLINK, INVERT, STRIKETHROUGH)
    styles_names_list = ("Bold", "Dim", "Italic", "Underline", "Blink", "Invert", "Strikethrough")

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
        Returns the text with the colour code before and the reset code after it

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
    menu_history_names = []
    menu_history_input = []
    pre_input = []


menu_manager = MenuManager()


def clear() -> None:
    """
    Clears the screen
    """
    # Check if GUI clear
    if display_type == "GUI":
        eel.clear_screen()
    else:
        os.system("cls")


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
    page_number = 1
    items_per_page = max_menu_items_per_page
    time_limit = 0

    def __init__(self, title: str, items: list | tuple, multi_dimensional: bool = False) -> None:
        """
        Creates a menu object

        @param title: The title of the menu
        @param items: The items in the menu, if multi_dimensional is True then the items should be a list of lists
        @param multi_dimensional: If the menu items array is multi-dimensional (i.e. has a value for each item)
        """
        self.title = title
        self.items = items
        self.multi_dimensional = multi_dimensional
        menu_manager.menu_history_names.append(title)

    def show_menu(self) -> list:
        """
        Prints the menu to a clear screen. Automatically uses the multi_dimensional variable to determine if the menu
        should use show_menu_double or show_menu
        """
        menu_items = self.items

        # Check if the screen should be cleared
        if self.clear_screen:
            # Clear the screen
            clear()

        # Print the menu
        render_text(divider)
        text_in_divider(" " + self.title, self.wrap_mode)
        if self.multi_dimensional:
            show_menu_double(menu_items, self.wrap_mode)
        else:
            show_menu(menu_items, self.wrap_mode)

        return menu_items

    def get_input(self, user_input: str = None) -> str:
        """
        Prints the menu to a clear screen and then gets the user input as an index of the menu items. Then stores the
        item in the user_input variable. If the user input is invalid then it will ask the user to try again until it
        is valid. Valid input is an integer between 0 and the length of the menu items array, or a string that is in
        the menu items array. If input is passed in then it will not ask the user for input and will instead use the
        input passed in (if it is not valid then it will ask). If the time_limit is set to a value greater than 0 then
        it will return after the time limit has been reached (if the user has not input anything before that).
        Pre-input allows for the user to input a list of indexes that will be automatically used as the user input.

        @param user_input: The user input to use instead of getting input from the user.
        @return: The option the user selected (the item in the menu items array)
        """

        menu_items = self.show_menu()

        used_pre_input = False

        # Check if the menu has a pre-input
        if len(menu_manager.pre_input) > 0:
            debug_message(f"Using pre-input ({menu_manager.pre_input[0]}) from {menu_manager.pre_input}")
            user_input = menu_manager.pre_input[0]
            used_pre_input = True
            menu_manager.pre_input.pop(0)

        # Calculate the possible options
        if self.multi_dimensional:
            input_items = menu_items[0]
        else:
            input_items = menu_items

        options = [*range(len(input_items))]

        input_prompt = "Choose an option (" + str(options[0]) + "-" + str(options[len(options) - 1]) + ")"
        # First input allows for the user to input a list of indexes that will be automatically used as the user input
        if not used_pre_input:

            # Check that input has been passed in
            if user_input is None:
                user_input = get_input(input_prompt)

            # Check if the user is wanting to do pre-input (i.e a list of indexes "1,4,3,2")
            if "," in user_input:
                # Split the string into a list
                user_input = user_input.split(",")

                # Store the pre-input
                menu_manager.pre_input = user_input

                # Re-Run with the first pre-input
                return self.get_input()

        user_input = get_user_input_of_type(int, input_prompt, options, input_items, self.time_limit, user_input)

        # Convert any indexes to the actual item
        if user_input in options:
            user_input = input_items[user_input]

        # Store the input
        self.user_input = user_input

        # Add the input to the input history
        menu_manager.menu_history_input.append(self.user_input)

        return self.user_input

    def get_input_option(self, type_to_convert: object, input_message: str = "",
                         must_be_one_of_these: list | tuple = None,
                         allow_these: list | tuple = None, max_time: int = 0) -> object:
        """
        Get user input of a specific type, if the input is not of the correct type then the user will be asked to
        re-enter until they do. Will check the menu for pre-input, if there is pre-input then it will use that
        instead of asking the user. Does not allow for pre input to start here, only to continue.

        @param type_to_convert: The type to convert the input to
        @param input_message: The message to display to the user (then " > ") (By default: "")
        @param must_be_one_of_these: If the input must be one of these values then enter them here (By default: None)
        @param allow_these: Allow input of these items (Not type specific) (checked first so 'must_be_one_of_these'
                doesn't apply to these items) (By default: None)
        @param max_time: The maximum time the user has to enter input (in seconds) (0, for no limit) (By default: 0)
        @return:
        """
        user_input = None

        # Check if the menu has a pre-input
        if len(menu_manager.pre_input) > 0:
            debug_message(f"Using pre-input ({menu_manager.pre_input[0]}) from {menu_manager.pre_input}")
            user_input = menu_manager.pre_input[0]
            menu_manager.pre_input.pop(0)

        # First input allows for the user to input a list of indexes that will be automatically used as the user input
        if user_input is None:
            user_input = get_input(input_message)

            # Check if the user is wanting to do pre-input (i.e a list of indexes "1,4,3,2")
            if "," in user_input:
                # Split the string into a list
                user_input = user_input.split(",")

                # Store the pre-input
                menu_manager.pre_input = user_input

                # Re-Run with the first pre-input
                return self.get_input_option()

        user_input = get_user_input_of_type(type_to_convert, input_message, must_be_one_of_these, allow_these,
                                            self.time_limit, user_input)

        # Store the input
        self.user_input = user_input

        # Add the input to the input history
        menu_manager.menu_history_input.append(self.user_input)

        return self.user_input


# - - - - - - - Functions - - - - - - -#


def text_in_divider(item_to_print: str, wrap: WrapMode = WrapMode.TRUNCATE) -> None:
    """
    Prints the item in between two divider symbols and wraps the text if it is too long by default using Truncate but
    will use whatever is passed in the wrap parameter.

    @param item_to_print: The text to print
    @param wrap: How the text should be wrapped if it is too long (Truncate by default)
    @return: None
    """
    text_length = len(Colour.clean_text(item_to_print))
    console_space_free = console_width - (divider_symbol_size * 2)

    # If the text is longer than the console width then wrap it
    if text_length > console_space_free:
        match wrap:
            case WrapMode.CHAR:
                # Print the current text in the divider, cutting off the text at the console width
                render_text(divider_symbol + item_to_print[:console_space_free] + divider_symbol)

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
                        render_text(divider_symbol + item_to_print[:console_space_free] + divider_symbol)
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
                render_text(divider_symbol + item_to_print + divider_symbol)

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
    render_text(divider_symbol + item_to_print + " " * width_left + divider_symbol)


def show_menu(menu_items: list, wrap: WrapMode = WrapMode.TRUNCATE) -> None:
    """
    Prints a divider at the start and end of the menu. Then prints the menu items and their index in the middle using
    the text_in_divider function for each item with the wrap mode passed in.

    @param wrap: How the text should be wrapped if it is too long (Truncate by default)
    @param menu_items: The list of menu items to print
    """
    render_text(divider)

    # Loop through all the items in the menu
    for x in range(len(menu_items)):
        item_to_print = " [" + str(x) + "]" + " " + menu_items[x]
        text_in_divider(item_to_print, wrap)
    render_text(divider)


def show_menu_double(menu_items: list, wrap: WrapMode = WrapMode.TRUNCATE) -> None:
    """
    Prints the menu item from the first array and its index on the left. On the right it prints the item from the
    second array. This is sandwiched inbetween two dividers. The item is wrapped if it is longer than
    half the console width, allowing space for the divider and the value.

    @param wrap: How the text should be wrapped if it is too long (Truncate by default)
    @param menu_items: The list of menu items to print
    """
    # TODO: Double Wrap
    render_text(divider)

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
        width_left = console_width - len(Colour.clean_text(item_to_print_1)) - len(
            Colour.clean_text(item_to_print_2)) - 2
        spacing = " " * width_left

        # Combine the two items
        final_item_to_print = divider_symbol + item_to_print_1 + spacing + item_to_print_2 + divider_symbol
        render_text(final_item_to_print)

    render_text(divider)


def print_text_on_same_line(text_to_print: str) -> None:
    """
    Prints the text on the same line as the last text printed. It first writes a blank line the length of the console
    to clear the line. Then it prints the text using the return character to overwrite the previous text.

    @param text_to_print: The text to print
    """
    # Clear the line
    sys.stdout.write('\r' + " " * console_width)

    # Print the text
    sys.stdout.write('\r' + text_to_print)


def render_text(text: str) -> None:
    if display_type == "CLI":
        print(text)
    elif display_type == "GUI":
        eel.print(str(text))


def get_input(prompt):
    if display_type == "CLI":
        return input(prompt)
    elif display_type == "GUI":
        user_input = ""
        while user_input == "":
            user_input = eel.get_input(prompt)()
            time.sleep(.1)
        eel.clear_input_buffer()
        return user_input


if display_type == "GUI":
    eel.init("web")
    # Thread index.html
    threading.Thread(target=eel.start, args=("index.html",),
                     kwargs={"width": 1800, "height": 600, "mode": "chrome"}).start()
