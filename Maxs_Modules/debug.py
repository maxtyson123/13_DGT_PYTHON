# - - - - - - - Imports - - - - - - -#
import time

# - - - - - - - Variables - - - - - - -#
debug_ignore = []


# - - - - - - - Functions - - - - - - -#

def debug(debug_message: str, log_type: str = "info") -> None:
    from Maxs_Modules.renderer import Colour

    """
    Print a debug message if the log type is not in the debug_ignore array
    @param debug_message: The debug message to print
    @param log_type: The type of log to print
    """

    if log_type not in debug_ignore:
        print(Colour.warning + "[DEBUG]" + log_type + Colour.RESET + " : " + debug_message)


def error(error_message: str) -> None:
    from Maxs_Modules.renderer import Colour
    """
    Print an error message and then wait 2 seconds
    @param error_message: The error message to print
    """
    print(Colour.error + "ERROR: " + error_message + Colour.RESET)
    time.sleep(2)
