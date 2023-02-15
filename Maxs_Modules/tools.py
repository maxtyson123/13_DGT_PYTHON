# - - - - - - - Imports - - - - - - -#
from Maxs_Modules.debug import error

# - - - - - - - Functions - - - - - - -#


def sort_multi_array(data: list, descending: bool = False) -> list:
    """
    Sorts a multi-dimensional array by the second value in each array using lambda shorthand, returns a copy of the list
    instead of sorting the original incase caller wants to keep the original list

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


def strBool(text: str) -> bool:
    """
    A replacement for the built-in bool function that allows for the conversion of a string with the text
    "True/False" to a bool

    @param text: The text to convert to a bool
    @return: The bool value of the text. Value Error if the text is not "True" or "False"
    """
    # Note: strBool is a replacement for the built-in bool function as when using bool() to convert a string to a
    # bool it will return True if there is any text in the string and False if there isn't, however I need it to
    # return True if the string is "True" and False if the string is "False"
    # Note: Do not use this when loading from JSON as the JSON module will convert the string to a bool
    if text == "True":
        return True
    elif text == "False":
        return False
    else:
        raise ValueError()


def get_user_input_of_type(type_to_convert: object, input_message: str = "", must_be_one_of_these: list = None,
                           allow_these: list = None) -> object:
    """
    Get user input of a specific type, if the input is not of the correct type then the user will be asked to re-enter
     until they do.

    @param type_to_convert: The type to convert the input to
    @param input_message: The message to display to the user (then " > ") (By default: "")
    @param must_be_one_of_these: If the input must be one of these values then enter them here (By default: None)
    @param allow_these: Allow input of these items (Not type specific) (checked first so 'must_be_one_of_these' doesn't
                         apply to these items) (By default: None)
    @return: The user input converted to the type specified
    """
    while True:
        user_input = input(input_message + " > ")

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
                    error("Invalid input, please enter one of these: " + str(must_be_one_of_these))
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


def try_convert(variable: object, type_to_convert: object, supress_errors: bool = False) -> object:
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

