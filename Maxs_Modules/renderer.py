# - - - - - - - Imports - - - - - - -#


import os
import sys
import time

from Maxs_Modules.debug import error, debug_cli, debug_message, in_ide
from Maxs_Modules.tools import try_convert, install_package

# - - - - - - - Variables - - - - - - -#


console_width = 100
divider_symbol = "#"
divider_symbol_size = len(divider_symbol)
divider = divider_symbol * console_width
menu_manager = None
max_menu_items_per_page = 10
imported_timeout = False


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
        # Store menu_items as a local variable as it can be changed if the menu is split into pages
        menu_items = self.get_pages()

        # Check if the screen should be cleared
        if self.clear_screen:
            # Clear the screen
            clear()

        # Print the menu
        print(divider)
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

        # Store the start time
        start_time = time.time()

        # Check if the menu has a pre-input
        if len(menu_manager.pre_input) > 0:

            debug_message(f"Using pre-input ({menu_manager.pre_input[0]}) from {menu_manager.pre_input}")

            valid = menu_manager.pre_input[0] < len(menu_items)

            # Check if the pre-input is a valid option index for this menu (multi-dimensional)
            if self.multi_dimensional:
                valid = menu_manager.pre_input[0] < len(menu_items[0])

            # Check if the pre-input is a valid option index for this menu
            if valid:

                # Store the input
                if self.multi_dimensional:
                    self.user_input = menu_items[0][menu_manager.pre_input[0]]
                else:
                    self.user_input = menu_items[menu_manager.pre_input[0]]

                # Remove the pre-input
                menu_manager.pre_input.pop(0)

                # Add the input to the input history
                menu_manager.menu_history_input.append(self.user_input)

                # Return
                return None

            else:
                # Print an error
                error("The pre-input (" + str(menu_manager.pre_input[0]) + ") was not a valid option for this menu ")

                # Clear the pre-input
                menu_manager.pre_input = []

        # Calculate the possible options
        if self.multi_dimensional:
            input_items = menu_items[0]
        else:
            input_items = menu_items

        options = [*range(len(input_items))]

        # Get the user input and validate it, note cant use the get_user_input_of_type function as the menu also
        # allows for "pre-input" and choosing an item index or the item itself
        while True:

            # If there is no input then get the input
            if user_input is None:
                input_prompt = "Choose an option (" + str(options[0]) + "-" + str(options[len(options) - 1]) + ") > "

                # Check if there is a time limit and since inputimeout doesn't work in the IDE, check if the program is
                # running in the IDE
                if self.time_limit != 0 and not in_ide:

                    install_package("inputimeout")
                    from inputimeout import inputimeout, TimeoutOccurred

                    # Check if the time limit has been reached
                    if time.time() - start_time > self.time_limit:
                        self.user_input = None
                        return None

                    # Calculate the time left
                    time_left = self.time_limit - (time.time() - start_time)

                    # Get the user input
                    try:
                        user_input = inputimeout(prompt=input_prompt, timeout=time_left)
                    except TimeoutOccurred:
                        self.user_input = None
                        return None
                else:
                    user_input = input(input_prompt)

            # If there is a type error then its returned as None otherwise it is the converted value
            if try_convert(user_input, int, True) is not None:  # Is an int

                # Convert the input to an int
                user_input = try_convert(user_input, int)
                if user_input in options:
                    self.user_input = input_items[user_input]
                    break
                else:
                    error("Invalid input, please enter one of these: " + str(options))
                    user_input = None

            # Not an int, so try
            else:
                # Check if it is a debug command
                if "debug" in user_input:
                    command = user_input.split(" ")

                    # Check if there is a command and if there is then remove the "debug" part and pass the rest to the
                    if len(command) > 1:
                        command.pop(0)

                    debug_cli(command)
                    user_input = None
                    continue

                # Check if the user is wanting to do pre-input (i.e a list of indexes "1,4,3,2")
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
                        if menu_manager.pre_input[0] < len(input_items):
                            self.user_input = input_items[menu_manager.pre_input[0]]
                        else:
                            error("Invalid pre-input, not an option")
                            menu_manager.pre_input = []
                            user_input = None
                            continue

                        # Remove the first input from the pre-input
                        menu_manager.pre_input.pop(0)

                        # Add the input to the input history
                        menu_manager.menu_history_input.append(self.user_input)

                        # Return
                        return self.user_input

                    else:
                        error("Invalid pre-input, please enter a list of numbers separated by commas")
                        user_input = None
                        continue

                # Check if the user inputted an allowed string
                if user_input in input_items:
                    self.user_input = user_input
                    break
                else:
                    error("Invalid input")
                    user_input = None
                    continue

        menu_manager.menu_history_input.append(self.user_input)
        return self.user_input

    def get_pages(self) -> list:
        """
        Splits the menu items into pages if there are more than the max menu items in the list of items. Curently not
        working will be fixed or removed later

        @return: The current page of menu items (a list of 10 options, including previous and next page)
        """

        # TODO: Will finish pages later if I have time but right now they are not working
        return self.items

        # Store menu_items as a local variable as don't want to change the original
        menu_items = self.items.copy()
        menu_items_count = len(menu_items)
        if self.multi_dimensional:
            menu_items_count = len(menu_items[0])

        # Check if the items have to be split into pages
        if menu_items_count > self.items_per_page:
            # Get the items for the current page
            slice_start = (self.page_number - 1) * self.items_per_page
            slice_end = (self.page_number * self.items_per_page)

            # Check if the "Previous Page" option is going to be added, if so need to remove one from the slice end
            # to ensure the max items per page is not exceeded
            if self.page_number > 1:
                slice_start -= 1

                if self.multi_dimensional:
                    menu_items[0].insert(slice_start, "Previous Page")
                    menu_items[1].insert(slice_start, str(self.page_number - 1))
                else:
                    menu_items.insert(slice_start, "Previous Page")

            # Check if the "Next Page" option is going to be added, if so need to minus 1 from the slice end
            if menu_items_count > slice_end:
                if self.multi_dimensional:
                    menu_items[0].insert(slice_end, "Next Page")
                    menu_items[1].insert(slice_end, str(self.page_number + 1))
                else:
                    menu_items.insert(slice_end, "Next Page")

                slice_end += 1

            # If the menu is multidimensional, then the items are stored in a list of lists and both arrays need to be
            # sliced
            if self.multi_dimensional:
                menu_items[0] = menu_items[0][slice_start: slice_end]
                menu_items[1] = menu_items[1][slice_start: slice_end]
            else:
                menu_items = menu_items[slice_start: slice_end]

        return menu_items


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
    Prints a divider at the start and end of the menu. Then prints the menu items and their index in the middle using
    the text_in_divider function for each item with the wrap mode passed in.

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
    Prints the menu item from the first array and its index on the left. On the right it prints the item from the
    second array. This is sandwiched inbetween two dividers. The item is wrapped if it is longer than
    half the console width, allowing space for the divider and the value.

    @param wrap: How the text should be wrapped if it is too long (Truncate by default)
    @param menu_items: The list of menu items to print
    """
    # TODO: Double Wrap
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
        width_left = console_width - len(Colour.clean_text(item_to_print_1)) - len(
            Colour.clean_text(item_to_print_2)) - 2
        spacing = " " * width_left

        # Combine the two items
        final_item_to_print = divider_symbol + item_to_print_1 + spacing + item_to_print_2 + divider_symbol
        print(final_item_to_print)

    print(divider)


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
