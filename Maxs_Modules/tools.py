# - - - - - - - Imports - - - - - - -#
import time


# - - - - - - - Functions - - - - - - -#

def strBool(text):
    # Note: strBool is a replacement for the built-in bool function as when using bool() to convert a string to a
    # bool it will return True if there is any text in the string and False if there isnt, however I need it to
    # return True if the string is "True" and False if the string is "False"
    # Note: Do not use this when loading from JSON as the JSON module will convert the string to a bool
    if text == "True":
        return True
    elif text == "False":
        return False
    else:
        raise ValueError()


def get_user_input_of_type(type_to_convert, input_message="", must_be_one_of_these=None):
    while True:
        user_input = input(input_message+" > ")
        user_input = try_convert(user_input, type_to_convert)

        if user_input is not None:
            if must_be_one_of_these is not None:
                if user_input in must_be_one_of_these:
                    return user_input
                else:
                    error("Invalid input, please enter one of these: " + str(must_be_one_of_these))
            else:
                return user_input


def set_if_none(variable, value):
    if variable is None:
        variable = value

    return variable


def try_convert(variable, type_to_convert):
    if variable is None:
        return None

    try:
        return type_to_convert(variable)
    except ValueError:
        error("Invalid input")
        return None


def error(error_message):
    print(error_message)
    time.sleep(2)


def debug(debug_message, log_type="info"):
    print("[DEBUG] : " + debug_message)
