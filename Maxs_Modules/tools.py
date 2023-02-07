import time


def error(error_message):
    print(error_message)
    time.sleep(2)


def debug(debug_message, log_type="info"):
    print("[DEBUG] : " + debug_message)


def validate_user_input_number(user_input):
    try:
        int(user_input)  # try to convert to int
        return True
    except ValueError:  # if it cant the return error
        error("Invalid input, please enter a number")
        return False