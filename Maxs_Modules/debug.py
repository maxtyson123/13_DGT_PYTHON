# - - - - - - - Imports - - - - - - -#
import time
# - - - - - - - Variables - - - - - - -#
use_debug = True
initialised_debug = False
debugger = None

session_message_log = []
session_error_log = []


# - - - - - - - Classes - - - - - - -#
def init_debug() -> None:
    """
    Initialise the debug system
    """
    global debugger
    global initialised_debug

    from Maxs_Modules.tools import try_convert, set_if_none
    from Maxs_Modules.files import SaveFile

    class Debug(SaveFile):

        # Logs
        log_ignore = []
        full_message_log = []
        full_error_log = []
        store_logs = False  # Weather or not to store the logs on file (under full...)
        max_log_history = 100  # The maximum amount of logs to store
        save_logs_location = "ProgramData/Logs"
        individual_log_files = False  # Weather or not to save the logs in individual files

        def __init__(self) -> None:
            """
            Create a new Debug object, loaded from debug.json
            """

            # Load from file
            super().__init__("ProgramData/debug.json")

            # Load the data from the save file
            self.log_ignore = try_convert(self.save_data.get("log_ignore"), list)
            self.full_message_log = try_convert(self.save_data.get("full_message_log"), list)
            self.full_error_log = try_convert(self.save_data.get("full_error_log"), list)
            self.store_logs = try_convert(self.save_data.get("store_logs"), bool)
            self.max_log_history = try_convert(self.save_data.get("max_log_history"), int)
            self.save_logs_location = try_convert(self.save_data.get("save_logs_location"), str)
            self.individual_log_files = try_convert(self.save_data.get("individual_log_files"), bool)

            # Load the default values if the data is not found
            self.load_defaults()

        def load_defaults(self) -> None:
            """
            Load the default values for the debug data
            """

            self.log_ignore = set_if_none(self.log_ignore, [])
            self.full_message_log = set_if_none(self.full_message_log, [])
            self.full_error_log = set_if_none(self.full_error_log, [])
            self.store_logs = set_if_none(self.store_logs, False)
            self.max_log_history = set_if_none(self.max_log_history, 100)
            self.save_logs_location = set_if_none(self.save_logs_location, "ProgramData/Logs")
            self.individual_log_files = set_if_none(self.individual_log_files, False)

        def log(self, message: str, log_type: str = "info") -> None:
            from Maxs_Modules.renderer import Colour

            """
            Print a debug message if the log type is not in the debug_ignore array
            @param debug_message: The debug message to print
            @param log_type: The type of log to print
            """

            if log_type not in self.log_ignore:
                print(Colour.warning + "[DEBUG] (" + log_type + ")" + Colour.RESET + " : " + message)
                session_message_log.append(message)

        def handle(self, command) -> None:
            """
            Shows a menu allowing the user to change the debug settings and see some values
            """

            match command:
                case "log_ignore_add":
                    self.log_ignore.append(get_user_input_of_type(str, "Log type to ignore: "))

                case "log_ignore_remove":
                    item_to_remove = get_user_input_of_type(str, "Log type to remove: ")
                    if item_to_remove in self.log_ignore:
                        self.log_ignore.remove(item_to_remove)

                case "store_logs":
                    from Maxs_Modules.renderer import Colour
                    self.store_logs = get_user_input_of_type(strBool, "Store the logs on file?  " +
                                                             Colour.true_or_false_styled())
                case "log_history_max":
                    self.max_log_history = get_user_input_of_type(int, "Max log history: ")

                case "log_save_location":
                    self.save_logs_location = get_user_input_of_type(str, "Log save location: ")

                case "log_individual_files":
                    self.individual_log_files = get_user_input_of_type(strBool, "Individual log files?  " +
                                                                       Colour.true_or_false_styled())
                case "logs":
                    print(session_message_log)
                    input("Enter to continue...")

                case "errors":
                    print(session_error_log)
                    input("Enter to continue...")

                case "logs_full":
                    print(self.full_message_log)
                    input("Enter to continue...")

                case "errors_full":
                    print(self.full_error_log)
                    input("Enter to continue...")

        def save(self) -> None:
            """
            Save the debug data to the save file
            """
            self.save_data = self.__dict__

            super().save()

        def close_debug_session(self):
            """
            Save the logs and then save to the file.
            """
            if self.store_logs:

                # Check if the logs are full
                if len(self.full_message_log) > self.max_log_history:
                    # Remove the oldest log
                    self.full_message_log.pop(0)
                if len(self.full_error_log) > self.max_log_history:
                    # Remove the oldest log
                    self.full_error_log.pop(0)

                # Add the session logs to the full logs
                self.full_message_log.append(session_message_log)
                self.full_error_log.append(session_error_log)

                # TODO: Save the logs to a file

            self.save()

    if use_debug:
        initialised_debug = True
        debugger = Debug()


# - - - - - - - Functions - - - - - - -#

def show_debug_menu(command : str) -> None:
    """
    If the debugger is initialized and debug is enabled, show the debug menu
    """
    if initialised_debug and debugger is not None:
        debugger.menu(command)


def debug_message(message: str, log_type: str = "info") -> None:
    """
    If the debugger is initialized and debug is enabled, print a debug message
    @param message: The debug message to print
    @param log_type: The type of log to print
    """
    if initialised_debug and debugger is not None:
        debugger.log(message, log_type)


def error(error_message: str) -> None:
    from Maxs_Modules.renderer import Colour
    """
    Print an error message and then wait 2 seconds
    @param error_message: The error message to print
    """
    print(Colour.error + "ERROR: " + error_message + Colour.RESET)

    if use_debug:
        session_error_log.append(error_message)

    time.sleep(2)
