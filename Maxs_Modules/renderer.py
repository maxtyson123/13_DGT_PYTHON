# - - - - - - - Imports - - - - - - -#
import os
import re
import signal
import sys
import time
import eel

from Maxs_Modules.debug import debug_message, in_ide
from Maxs_Modules.files import UserData
from Maxs_Modules.tools import get_user_input_of_type

# - - - - - - - Variables - - - - - - -#
# DONT CHANGE
DISPLAY_TYPE = UserData().display_mode

# CHANGE IN IDLE
COMPACT_CONSOLE = False
ANSI_COLOURS_ENABLED = True

# CHANGE IF DESIRED
CONSOLE_WIDTH = 100
CONSOLE_SYMBOL = chr(9617)  # OR use '░'
# Note change this to be False to disable auto htmlify (leave the DISPLAY_TYPE == "GUI" part)
CONVERT_OUTPUT_TO_HTML = True and DISPLAY_TYPE == "GUI"
ADD_COLOUR_TO_TEXT = True

if COMPACT_CONSOLE:
    CONSOLE_SYMBOL = "-"
DIVIDER_SYMBOL_SIZE = len(CONSOLE_SYMBOL)
DIVIDER = CONSOLE_SYMBOL * CONSOLE_WIDTH
menu_manager = None


# - - - - - - - Classes - - - - - - -#
class WrapMode:
    """
    A class that stores shorthands for the styling to preform when text is larger than the console width
    """
    NONE = 0
    CHAR = 1
    WORD = 2
    TRUNCATE = 3


class Colour:
    """
    A class that stores the colour codes for the different colours.
    Note: from https://en.wikipedia.org/wiki/ANSI_escape_code
    """
    # Colours
    BLACK = "\033[30m" if ANSI_COLOURS_ENABLED else ""
    RED = "\033[31m" if ANSI_COLOURS_ENABLED else ""
    GREEN = "\033[32m" if ANSI_COLOURS_ENABLED else ""
    YELLOW = "\033[33m" if ANSI_COLOURS_ENABLED else ""
    BLUE = "\033[34m" if ANSI_COLOURS_ENABLED else ""
    MAGENTA = "\033[35m" if ANSI_COLOURS_ENABLED else ""
    CYAN = "\033[36m" if ANSI_COLOURS_ENABLED else ""
    WHITE = "\033[37m" if ANSI_COLOURS_ENABLED else ""
    GREY = "\033[90m" if ANSI_COLOURS_ENABLED else ""

    colours_list = (BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, GREY)
    colours_names_list = ("Black", "Red", "Green", "Yellow", "Blue", "Magenta", "Cyan", "White", "Grey")

    # Styles
    BOLD = "\033[1m" if ANSI_COLOURS_ENABLED else ""
    DIM = "\033[2m" if ANSI_COLOURS_ENABLED else ""
    ITALIC = "\033[3m" if ANSI_COLOURS_ENABLED else ""
    UNDERLINE = "\033[4m" if ANSI_COLOURS_ENABLED else ""
    BLINK = "\033[5m" if ANSI_COLOURS_ENABLED else ""
    INVERT = "\033[7m" if ANSI_COLOURS_ENABLED else ""
    STRIKETHROUGH = "\033[9m" if ANSI_COLOURS_ENABLED else ""

    styles_list = (BOLD, DIM, ITALIC, UNDERLINE, BLINK, INVERT, STRIKETHROUGH)
    styles_names_list = ("Bold", "Dim", "Italic", "Underline", "Blink", "Invert", "Strikethrough")

    # Reset
    RESET = "\033[0m" if ANSI_COLOURS_ENABLED else ""

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
    if DISPLAY_TYPE == "GUI":
        eel.clear_screen()
    else:
        if not in_ide:
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
    time_limit = 0

    def __init__(self, title: str, items: list | tuple, multi_dimensional: bool = False) -> None:
        """
        Creates a menu object

        @param title: The title of the menu
        @param items: The items in the menu, if multi_dimensional is True then the items should be a list of lists
        @param multi_dimensional: If the menu items array is multidimensional (i.e. has a value for each item)
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
        render_header(self.title, False)

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

        # Check if the menu has a pre-input
        if len(menu_manager.pre_input) > 0:
            debug_message(f"Using pre-input ({menu_manager.pre_input[0]}) from {menu_manager.pre_input}")
            user_input = menu_manager.pre_input[0]
            menu_manager.pre_input.pop(0)

        # Calculate the possible options
        if self.multi_dimensional:
            input_items = menu_items[0]
        else:
            input_items = menu_items

        options = [*range(len(input_items))]

        input_prompt = "Choose an option (" + str(options[0]) + "-" + str(options[len(options) - 1]) + ")"

        user_input = get_user_input_of_type(int, input_prompt, options, input_items, self.time_limit, user_input, True)

        # Check if the user input is an array
        if isinstance(user_input, list):
            # Store the pre-input
            menu_manager.pre_input = user_input

            # Re-Run with the first pre-input
            return self.get_input()

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

        user_input = get_user_input_of_type(type_to_convert, input_message, must_be_one_of_these, allow_these,
                                            self.time_limit, user_input, True)

        # Check if the user input is an array
        if isinstance(user_input, list):
            # Store the pre-input
            menu_manager.pre_input = user_input

            # Re-Run with the first pre-input
            return self.get_input_option(type_to_convert, input_message, must_be_one_of_these, allow_these, max_time)

        # Store the input
        self.user_input = user_input

        # Add the input to the input history
        menu_manager.menu_history_input.append(self.user_input)

        return self.user_input


# - - - - - - - Functions - - - - - - -#


def text_in_divider(item_to_print: str, wrap: WrapMode = WrapMode.TRUNCATE) -> None:
    """
    Prints the item in between two DIVIDER symbols and wraps the text if it is too long by default using Truncate but
    will use whatever is passed in the wrap parameter.

    @param item_to_print: The text to print
    @param wrap: How the text should be wrapped if it is too long (Truncate by default)
    @return: None
    """
    text_length = len(Colour.clean_text(item_to_print))
    console_space_free = CONSOLE_WIDTH - (DIVIDER_SYMBOL_SIZE * 2)

    # If the text is longer than the console width then wrap it
    if text_length > console_space_free:
        match wrap:
            case WrapMode.CHAR:
                # Print the current text in the DIVIDER, cutting off the text at the console width
                text = CONSOLE_SYMBOL + item_to_print[:console_space_free] + CONSOLE_SYMBOL
                render_text(text)

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
                    if len(Colour.clean_text(word)) > console_space_free:
                        # Join the words together
                        item_to_print = " ".join(words)

                        # Print the item in the DIVIDER, split at console width
                        render_text(CONSOLE_SYMBOL + item_to_print[:console_space_free] + CONSOLE_SYMBOL)
                        current_size += console_space_free

                        # Store the text to print as adding a space for readability. Cut off the text already written
                        # and ignore the padding space
                        item_to_print = " " + item_to_print[current_size:]

                        # Re-run the function as many times as needed and then return so the original, un wrapped,
                        # text isn't printed
                        text_in_divider(item_to_print, wrap)
                        return

                    # If the current size plus the word length is less than the console width
                    if current_size + len(Colour.clean_text(word)) < console_space_free:
                        # Add the word to the current size
                        current_size += len(Colour.clean_text(word))

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

                # Print the item in the DIVIDER
                render_text(CONSOLE_SYMBOL + item_to_print + CONSOLE_SYMBOL)

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
    render_text(CONSOLE_SYMBOL + item_to_print + Colour.RESET + " " * width_left + CONSOLE_SYMBOL)


def show_menu(menu_items: list, wrap: WrapMode = WrapMode.TRUNCATE) -> None:
    """
    Prints a DIVIDER at the start and end of the menu. Then prints the menu items and their index in the middle using
    the text_in_divider function for each item with the wrap mode passed in.

    @param wrap: How the text should be wrapped if it is too long (Truncate by default)
    @param menu_items: The list of menu items to print
    """
    if CONVERT_OUTPUT_TO_HTML:
        for x in range(len(menu_items)):
            item_to_print = f"<div class='menu-option'><button id='{x}' onclick='choose_item(this)'> <p " \
                            f"class='split_for_colour menu-item-main inline'>{menu_items[x]}</p><p " \
                            f"class='menu-item-secondary inline'></p></button></div>"
            render_text(item_to_print)
    else:
        render_text(DIVIDER)
        if not COMPACT_CONSOLE:
            text_in_divider("")

        # Loop through all the items in the menu
        for x in range(len(menu_items)):
            item_to_print = " [" + str(x) + "]" + " " + menu_items[x]
            text_in_divider(item_to_print, wrap)
        if not COMPACT_CONSOLE:
            text_in_divider("")
        render_text(DIVIDER)


def show_menu_double(menu_items: list, wrap: WrapMode = WrapMode.TRUNCATE) -> None:
    """
    Prints the menu item from the first array and its index on the left. On the right it prints the item from the
    second array. This is sandwiched between two dividers. The item is wrapped if it is longer than
    half the console width, allowing space for the DIVIDER and the value.

    @param wrap: How the text should be wrapped if it is too long (Truncate by default)
    @param menu_items: The list of menu items to print
    """

    if CONVERT_OUTPUT_TO_HTML:
        for x in range(len(menu_items[0])):
            item_to_print = f"<div class='menu-option'><button id='{x}' onclick='choose_item(this)'><p " \
                            f"class='split_for_colour menu-item-main inline'>{menu_items[0][x]}</p><p class='menu" \
                            f"-item-secondary " \
                            f"inline'>{menu_items[1][x]}</p></button></div>"
            render_text(item_to_print)
    else:
        render_text(DIVIDER)
        if not COMPACT_CONSOLE:
            text_in_divider("")
        # Loop through all the items in the menu
        for x in range(len(menu_items[0])):

            # Create the two items to print
            item_to_print_1 = " [" + str(x) + "]" + " " + menu_items[0][x]
            item_to_print_2 = "(" + menu_items[1][x] + ") "

            # Truncate the text if it is too long
            allowed_width = int(CONSOLE_WIDTH / 2)

            if len(Colour.clean_text(item_to_print_1)) > allowed_width:
                item_to_print_1 = item_to_print_1[:allowed_width - 2]  # Truncate the text to fit half the console width

            if len(Colour.clean_text(item_to_print_2)) > allowed_width:
                item_to_print_2 = item_to_print_1[:allowed_width - 2]  # Truncate the text to fit half the console width

            # Spacing between the two items (similar to how it is done in "text_in_divider" function)
            # The length of the text, minus console width, minus 2 for the border
            width_left = CONSOLE_WIDTH - len(Colour.clean_text(item_to_print_1)) - len(
                Colour.clean_text(item_to_print_2)) - 2
            spacing = " " * width_left

            # Combine the two items
            final_item_to_print = CONSOLE_SYMBOL + item_to_print_1 + Colour.RESET + spacing + item_to_print_2 + \
                                  Colour.RESET + CONSOLE_SYMBOL
            render_text(final_item_to_print)

        if not COMPACT_CONSOLE:
            text_in_divider("")
        render_text(DIVIDER)


def print_text_on_same_line(text_to_print: str) -> None:
    """
    Prints the text on the same line as the last text printed. It first writes a blank line the length of the console
    to clear the line. Then it prints the text using the return character to overwrite the previous text.

    @param text_to_print: The text to print
    """
    # Clear the line
    sys.stdout.write('\r' + " " * CONSOLE_WIDTH)

    # Print the text
    sys.stdout.write('\r' + text_to_print)


def auto_style_text(text: str, force: bool = False) -> str:
    """
    Automatically styles the text based on certain keywords. This is used to make the text more readable.
    Colours are automatically converted into their ANSI escape codes.

    @param text: The text to style
    @param force: Force the text to be styled even if auto_colour is False
    @return: The styled text
    """
    if not ADD_COLOUR_TO_TEXT and not force:
        return text

    if text is None:
        return text

    if "ERROR" in text:
        return Colour.RED + text + Colour.RESET

    # NOTE: Regex symbols: \b = word boundary, \d = digit, \s = whitespace, \w = word character, \B = not word boundary
    # \g = group, r' = raw string

    # Replace certain words with their colour (ignore case)
    text = re.compile(r'\btrue\b', re.IGNORECASE).sub(Colour.GREEN + r'\g<0>' + Colour.RESET, text)
    text = re.compile(r'\bcorrect\b', re.IGNORECASE).sub(Colour.GREEN + r'\g<0>' + Colour.RESET, text)
    text = re.compile(r'\bfalse\b', re.IGNORECASE).sub(Colour.RED + r'\g<0>' + Colour.RESET, text)
    text = re.compile(r'\bincorrect\b', re.IGNORECASE).sub(Colour.RED + r'\g<0>' + Colour.RESET, text)
    text = re.compile(r'\bnone\b', re.IGNORECASE).sub(Colour.YELLOW + r'\g<0>' + Colour.RESET, text)

    # Replace colours with their colour
    text = re.compile(r'\bblack\b', re.IGNORECASE).sub(Colour.BLACK + r'\g<0>' + Colour.RESET, text)
    text = re.compile(r'\bred\b', re.IGNORECASE).sub(Colour.RED + r'\g<0>' + Colour.RESET, text)
    text = re.compile(r'\bgreen\b', re.IGNORECASE).sub(Colour.GREEN + r'\g<0>' + Colour.RESET, text)
    text = re.compile(r'\byellow\b', re.IGNORECASE).sub(Colour.YELLOW + r'\g<0>' + Colour.RESET, text)
    text = re.compile(r'\bblue\b', re.IGNORECASE).sub(Colour.BLUE + r'\g<0>' + Colour.RESET, text)
    text = re.compile(r'\bmagenta\b', re.IGNORECASE).sub(Colour.MAGENTA + r'\g<0>' + Colour.RESET, text)
    text = re.compile(r'\bcyan\b', re.IGNORECASE).sub(Colour.CYAN + r'\g<0>' + Colour.RESET, text)
    text = re.compile(r'\bwhite\b', re.IGNORECASE).sub(Colour.WHITE + r'\g<0>' + Colour.RESET, text)

    return text


def render_text(text: str) -> None:
    """
    Prints the text to the console. If the display type is GUI then it will use the js function to print the text.
    @param text: The text to print
    """
    if DISPLAY_TYPE == "CLI":
        print(auto_style_text(text))
    elif DISPLAY_TYPE == "GUI":
        eel.print(str(auto_style_text(text)))


def get_input(prompt: str = "") -> str:
    """
    Gets the user input. If the display type is GUI then it will use the js function to get the input.
    Otherwise, it will use the normal input function.

    @param prompt: The prompt to display
    @return: The user input
    """
    # If the display type is CLI then use the normal input function
    if DISPLAY_TYPE == "CLI":
        return input(auto_style_text(prompt))

    # If the display type is GUI then use the js function to get the input
    elif DISPLAY_TYPE == "GUI":
        # Prompt for input
        eel.highlight_input()

        # Wait for the user to enter something
        user_input = ""
        while user_input == "":
            # Check for the user to have entered something
            user_input = eel.get_input(auto_style_text(prompt))()
            time.sleep(.1)

        # Clear amd return the input
        eel.clear_input_buffer()

        # Convert nothing into None
        if user_input == "" or user_input == " ":
            user_input = None

        return user_input


def get_gui_timed_input(prompt: str, timeout: int) -> str:
    """
    Gets the user input using the GUI, but with a timeout. If the user does not enter anything within the timeout then
    it will return None.

    @param prompt: The prompt to display
    @param timeout: The timeout in seconds
    @return: The user input
    """
    # Store start info
    user_input = ""
    start_time = time.time()

    # Loop until the user has entered something or the time has been reached
    while user_input == "" and time.time() - start_time < timeout:
        user_input = eel.get_input(prompt)()
        time.sleep(.1)

    # Grab and clear the input buffer
    user_input = eel.force_get_input()()
    eel.clear_input_buffer()

    # Convert nothing into None
    if user_input == "" or user_input == " ":
        user_input = None

    # Return the input
    return user_input


def render_header(title: str, enclose_bottom: bool = True) -> None:
    """
    Renders a title header to the console or GUI.

    @param title: The title to display
    @param enclose_bottom: Whether to enclose the bottom of the header with a border (CLI only)
    """
    if DISPLAY_TYPE == "GUI":
        eel.set_title(title)

    if CONVERT_OUTPUT_TO_HTML:
        render_text(f"<h2 class='menu-title'>{title}</h2>")
    else:
        # Print spacer and title
        render_text(DIVIDER)
        if not COMPACT_CONSOLE:
            text_in_divider("")

        text_in_divider(" " + title.center(CONSOLE_WIDTH - (DIVIDER_SYMBOL_SIZE * 2) - 1), WrapMode.WORD)

        if not COMPACT_CONSOLE:
            text_in_divider("")

        # Allow for a bottom border
        if enclose_bottom:
            render_text(DIVIDER)


def render_quiz_header(game: object) -> None:
    """
    Renders the quiz header to the console or GUI.
    @param game: The game object containing the quiz info
    """
    current_question = game.current_question + 1
    question_amount = game.question_amount
    user = game.users[game.current_user_playing].styled_name()
    time_limit = game.time_limit

    if CONVERT_OUTPUT_TO_HTML:
        render_text(f"<p class='question-header'>Question {current_question} of {question_amount} | User: {user} | "
                    f"Time Limit: {time_limit} seconds</p>")
    else:
        render_text(DIVIDER)
        if not COMPACT_CONSOLE:
            text_in_divider("")
        text_in_divider(f" Question {current_question} of {question_amount}")
        text_in_divider(f" User: {user}", WrapMode.WORD)
        text_in_divider(f" Time Limit: {time_limit} seconds")
        if not COMPACT_CONSOLE:
            text_in_divider("")


def round_to_decimal(number: float, decimal_places: int = 2) -> float:
    """
    Round a number to a certain amount of decimal places
    @param number: The number to round
    @param decimal_places: The amount of decimal places to round to
    @return: The rounded number
    """
    return round(number * (10 ** decimal_places)) / (10 ** decimal_places)


@eel.expose
def close_python() -> None:
    """
    Closes the python process and GUI window. This is used by the GUI to close the python process when the window is
    closed.
    """
    gui_close()
    print("Window closed, closing python...")
    # Get the process ID of the current process
    pid = os.getpid()

    # Kill the process and all its child threads
    os.kill(pid, signal.SIGTERM)


def init_gui() -> None:
    """
    If the display type is GUI then start the web server on a free port (starting at 8080)
    """
    # Import here to prevent circular imports
    from Maxs_Modules.network import get_free_port, get_ip

    # If the display type is GUI then start the web server
    if DISPLAY_TYPE == "GUI":
        web_ip = get_ip()
        web_port = get_free_port(web_ip, 8080)
        print(web_port)

        eel.init("web")
        eel.start("index.html", block=False,
                  port=web_port, host=web_ip)


def gui_close() -> None:
    """
    If the display type is GUI then close the window of the web server
    """
    # If the display type is GUI then close the web server
    if DISPLAY_TYPE == "GUI":
        eel.close_window()
