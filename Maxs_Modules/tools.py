# - - - - - - - Imports - - - - - - -#
import time

from Maxs_Modules.debug import error, debug_cli, in_ide

# - - - - - - - Variables - - - - - - -#
imported_timeout = False


# - - - - - - - Functions - - - - - - -#


def sort_multi_array(data: list, descending: bool = False) -> list:
    """
    Sorts a multi-dimensional array by the second value in each array using lambda shorthand, returns a copy of the list
    instead of sorting the original incase caller wants to keep the original list. If the descending parameter is set
    then the data will be sorted in reverse order. The second array in the list must be a list of numbers.

    @param data: The list to be sorted
    @param descending: Weather to sort in descending order or not. By default, this is False.
    @return: The sorted list (a copy of the original list)
    """

    # Unpack the data into two lists, one for the names and one for the scores
    names, scores = data[0], data[1]

    # Sort the data by the scores
    sorted_data = sorted(zip(names, scores), key=lambda x: x[1], reverse=descending)

    # Put the data back into the original format
    result = list(zip(*sorted_data))
    result = [list(r) for r in result]

    return result


def string_bool(text: str) -> bool:
    """
    A replacement for the built-in bool function that allows for the conversion of a string with the text
    "True/False" to a bool. It will raise a ValueError if the text is not "True" or "False" otherwise it will return
    the value.

    @note string_bool is a replacement for the built-in bool function as when using bool() to convert a string to a
    bool it will return True if there is any text in the string and False if there isn't, however I need it to return
    True if the string is "True" and False if the string is "False"

    @note: Do not use this when loading from JSON as the JSON module will convert the string to a bool

    @param text: The text to convert to a bool
    @return: The bool value of the text. Value Error if the text is not "True" or "False"
    """
    if text == "True":
        return True
    elif text == "False":
        return False
    else:
        raise ValueError()


def ip_address(text: str) -> Exception or str:
    """
    A type to use to check if the string is a valid IP address, if it is then the string will be returned,
    if it isn't than a ValueError will be raised. Must adhere to the IP address format of V4.

    @param text:  The text to check
    @return: True if the text is a valid IP address, False if it isn't
    """

    # Check if the text is a valid IP address
    if text.count(".") != 3:
        raise ValueError()

    # Check if the octets are valid
    for part in text.split("."):
        if not part.isdigit():
            raise ValueError()

        if not 0 <= int(part) <= 255:
            raise ValueError()

    return text


def get_user_input_of_type(type_to_convert: object, input_message: str = "", must_be_one_of_these: list | tuple = None,
                           allow_these: list | tuple = None, max_time: int = 0) -> object:
    """
    Get user input of a specific type, if the input is not of the correct type then the user will be asked to re-enter
    until they do.


    @param type_to_convert: The type to convert the input to
    @param input_message: The message to display to the user (then " > ") (By default: "")
    @param must_be_one_of_these: If the input must be one of these values then enter them here (By default: None)
    @param allow_these: Allow input of these items (Not type specific) (checked first so 'must_be_one_of_these' doesn't
                         apply to these items) (By default: None)
    @param max_time: The maximum time the user has to enter input (in seconds) (0, for no limit) (By default: 0)
    @return: The user input converted to the type specified
    """

    # Store the start time
    start_time = time.time()

    while True:

        # Check if there is a time limit and since inputimeout doesn't work in the IDE, check if the program is
        # running in the IDE
        if max_time != 0 and not in_ide:

            # Don't continuously import inputimeout, and there is no need to install it and import it if there is no
            # need for it yet
            install_package("inputimeout")

            from inputimeout import inputimeout, TimeoutOccurred

            # Check if the time limit has been reached
            if time.time() - start_time > max_time:
                return None

            # Calculate the time left
            time_left = max_time - (time.time() - start_time)

            # Get the user input
            try:
                user_input = inputimeout(prompt=input_message + " > ", timeout=time_left)
            except TimeoutOccurred:
                return None
        else:
            user_input = input(input_message + " > ")

        # Check if it is a debug command
        if "debug" in user_input:
            command = user_input.split(" ")

            # Check if there is a command and if there is then remove the "debug" part and pass the rest to the
            if len(command) > 1:
                command.pop(0)

            debug_cli(command)
            continue

        # Check if the user inputted an allowed string
        if allow_these is not None:
            if user_input in allow_these:
                return user_input

        user_input = try_convert(user_input, type_to_convert)

        # If there is a type error then its returned as None, so now we check if the user input is in the alternative
        # array
        if user_input is not None:
            if must_be_one_of_these is not None:
                if user_input in must_be_one_of_these:
                    return user_input
                else:
                    error("Invalid input")
            else:
                return user_input
        # Side note: No need to error here as the error will be called in the try_convert function


def set_if_none(variable: object, value: object) -> object:
    """
    Set a variable to a value if the variable is None

    @param variable: The variable to check if its None
    @param value: The value to set the variable to if its None
    @return: The variable
    """
    if variable is None:
        variable = value

    return variable


def try_convert(variable: object, type_to_convert: type, supress_errors: bool = False) -> object:
    """
    Try to convert a variable to a type, if it fails then return None

    @param variable: The variable to convert
    @param type_to_convert: The type to convert the variable to
    @param supress_errors: Weather to supress errors or not (By default: False)
    @return: The converted variable or None if it failed
    """
    if variable is None:
        return None

    try:
        return type_to_convert(variable)
    except ValueError:
        if not supress_errors:
            error("Invalid input")
        return None

packages_isntalled_this_session = []
def install_package(package: str) -> None:
    """
    Install a package using pip

    @param package: The package to install
    @return: None
    """
    try:
        if package in packages_isntalled_this_session:
            return
        import pip
        print("Installing package: " + package + "...")
        pip.main(["install", package, "--disable-pip-version-check", "--no-color", "--quiet"])
        packages_isntalled_this_session.append(package)
    except Exception as e:
        error("Failed to install package: " + package + " (" + str(e) + ")")
