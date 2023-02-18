# - - - - - - - Imports - - - - - - -#
import os
import time
from datetime import datetime

# - - - - - - - Variables - - - - - - -#
use_debug = True
initialised_debug = False
debugger = None

session_message_log = []
session_error_log = []


# - - - - - - - Classes - - - - - - -#
def init_debug() -> None:
    """
    Sets the debugger variable to a instance of the Debug class if the use_debug variable is True
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

        # Commands
        commands = ["help", "logs", "errors", "server"]
        handlers = [None, None, None, None]

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

            # Load the handlers
            self.handlers = [self.command_help, self.command_logs, self.command_errors, self.command_server]

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
            Print a debug message if the log type is not in the debug_ignore array and appends the message to the log
            @param debug_message: The debug message to print
            @param log_type: The type of log to print
            """

            if log_type not in self.log_ignore:
                print(Colour.warning + "[DEBUG] (" + log_type + ")" + Colour.RESET + " : " + message)
                session_message_log.append(message)

        def command_server(self, *args: tuple) -> None:

            from Maxs_Modules.network import test_echo_server, test_echo_client, get_ip

            if len(args) == 0:
                args = ["-h"]

            for arg in args:
                match arg:
                    case "-h":
                        print("Params:")
                        print(" -h: Shows this help message")
                        print(" -ip: Gets this devices ip address")
                        print(" -echo-server: Starts a test echo server")
                        print(" -echo-client: Starts a test echo client")

                    case "-ip":
                        print("IP: " + get_ip())

                    case "-echo-server":
                        test_echo_server()

                    case "-echo-client":
                        test_echo_client()

                    case _:
                        print("Unknown arg: " + arg)

        def command_help(self, *args: tuple) -> None:
            """
            Prints all the commands, if a command is given as an arg it will run the command with the -h arg
            @param args: The commands to run
            """

            # Default behaviour for no args
            if len(args) == 0:
                print("Some commands may support -h for more info")
                print("Commands:")
                for command in self.commands:
                    print(" - " + command)

            for arg in args:
                if arg in self.commands:
                    self.handlers[self.commands.index(arg)]("-h")
                else:
                    print("Unknown command: " + arg)

        def command_logs(self, *args: tuple) -> None:
            """
            Allows the user to view the logs, and change the settings. The default behaviour is to list the logs
            @param args: The args to pass to the command 
            """
            from Maxs_Modules.tools import get_user_input_of_type, strBool
            from Maxs_Modules.renderer import Colour

            # Default behaviour for no args
            if len(args) == 0:
                args = ["-list"]

            for arg in args:
                match arg:
                    case "-h":
                        print("Params:")
                        print(" -h: Shows this help message")
                        print(" -ignore-add: Adds a log type to ignore")
                        print(" -ignore-remove: Removes a log type to ignore")
                        print(" -ignore-list: Lists the log types to ignore")
                        print(" -ignore-clear: Clears the log types to ignore")
                        print(" -list: Lists current the logs")
                        print(" -list-full: List the full history of logs")
                        print(" -clear-history: Clears the full history of logs")
                        print(" -store: Sets weather or not to store the logs")
                        print(" -store-location: Sets the location to store the logs")
                        print(" -store-individual: Sets weather or not to store the logs in individual files")
                        print(" -store-max: Sets the maximum amount of logs to store")

                    case "-ignore-add":
                        self.log_ignore.append(get_user_input_of_type(str, "Log type to ignore: "))

                    case "-ignore-remove":
                        item_to_remove = get_user_input_of_type(str, "Log type to remove: ")

                    case "-ignore-list":
                        print("Log types to ignore:")
                        for log_type in self.log_ignore:
                            print(" - " + log_type)

                    case "-ignore-clear":
                        self.log_ignore = []

                    case "-list":
                        print("Current logs:")
                        for log in session_message_log:
                            print(" - " + log)

                    case "-list-full":
                        print("Full logs:")
                        for log in self.full_message_log:
                            print(" - " + str(log))

                    case "-store":
                        self.store_logs = get_user_input_of_type(strBool, "Store the logs on file?  " +
                                                                 Colour.true_or_false_styled())
                    case "-store-location":
                        self.save_logs_location = get_user_input_of_type(str, "Location to store the logs: ")

                    case "-store-individual":
                        self.individual_log_files = get_user_input_of_type(strBool,
                                                                           "Store the logs in individual files?  " +
                                                                           Colour.true_or_false_styled())

                    case "-store-max":
                        self.max_log_history = get_user_input_of_type(int, "Maximum amount of logs to store: ")

                    case "-clear-history":
                        self.full_message_log = []

                    case _:
                        print("Unknown command: " + arg)

        def command_errors(self, *args: tuple) -> None:
            """
            Allows the user to view/clear the errors (note: errors made by the error() funct, not the runtime errors)
            @param args: The args to pass to the command, if none are given it will show the help message
            """
            # Default behaviour for no args
            if len(args) == 0:
                args = ["-h"]

            for arg in args:
                match arg:
                    case "-h":
                        print("Params:")
                        print(" -h: Shows this help message")
                        print(" -list: Lists current the errors")
                        print(" -list-full: List the full history of errors")
                        print(" -clear-history: Clears the past errors")

                    case "-list":
                        print("Current errors:")
                        for log_error in session_error_log:
                            print(" - " + log_error)

                    case "-list-full":
                        print("Full errors:")
                        for log_error in self.full_error_log:
                            print(" - " + str(log_error))

                    case "-clear-history":
                        self.full_error_log = []

                    case _:
                        print("Unknown command: " + arg)

        def handle(self, user_input: list) -> None:
            """
            Attempts to run the handler for the command, and passes the args to the handler (as a tuple)
            """

            # Get the first word of the command
            command = user_input[0]

            # Get the reset of the words as the args
            args = user_input[1:]

            if command in self.commands:
                # Get the index of the command
                command_index = self.commands.index(command)

                # Run the handler for the command and pass the args
                self.handlers[command_index](*args)

        def save(self) -> None:
            """
            Save the debug data to the save file
            """
            self.save_data = self.__dict__
            self.save_data.pop("handlers")

            super().save()

        def close_debug_session(self):
            """
            Save the logs and then save to the file.
            """
            if self.store_logs:

                # Check if the logs are to be saved to the main debug file or the individual files

                if self.individual_log_files:

                    # Check if the save location exists
                    if not os.path.exists(self.save_logs_location):
                        os.makedirs(self.save_logs_location)

                    # Create the log name
                    log_name = "/log_" + str(datetime.now()).replace(":", "-").replace(" ", "_") + ".txt"

                    # Save the logs to the individual files
                    with open(self.save_logs_location + log_name, "w") as file:
                        file.write("Message log:\n"
                                   + str(session_message_log)
                                   + "\n\nError log:\n"
                                   + str(session_error_log))

                else:
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

            self.save()

    if use_debug:
        initialised_debug = True
        debugger = Debug()


# - - - - - - - Functions - - - - - - -#

def close_debug_session() -> None:
    """
    Save the logs and then save to the file.
    """
    if initialised_debug and debugger is not None:
        debugger.close_debug_session()


def show_debug_menu(command: list) -> None:
    """
    If the debugger is initialized and debug is enabled, show the debug menu
    """
    if initialised_debug and debugger is not None:
        debugger.handle(command)


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
