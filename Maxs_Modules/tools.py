import time


def error(error_message):
    print(error_message)
    time.sleep(2)


def debug(debug_message, log_type="info"):
    print("[DEBUG] : " + debug_message)