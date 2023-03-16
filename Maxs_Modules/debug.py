# - - - - - - - Imports - - - - - - -#
import os
import sys
import time
from datetime import datetime

# - - - - - - - Variables - - - - - - -#

maxs_debugger = None

session_message_log = []
session_error_log = []


# - - - - - - - Classes - - - - - - -#
def init_debug() -> None:
    """
    Sets the debugger variable to an instance of the Debug class if the use_debug variable is True
    """

    # No point in importing the debug class if the debugger is not being used
    if not use_debug:
        return

    # Make sure to be able to update the debugger variable, as using it as a global variable it has my name on it to
    # prevent it shadowing other modules
    global maxs_debugger

    # Import here to prevent circular imports
    from Maxs_Modules.tools import try_convert, set_if_none
    from Maxs_Modules.files import SaveFile

    # Create the debugger
    class Debug(SaveFile):

        # Logs
        log_ignore = []
        full_message_log = []
        full_error_log = []
        store_logs = False
        max_log_history = 100
        save_logs_location = "ProgramData/Logs"
        individual_log_files = False
        local_db = False

        # Commands
        commands = ("help", "logs", "errors", "server", "database")
        handlers = [None, None, None, None, None]

        def __init__(self) -> None:
            """
            Create a new Debug object, loaded from debug.json. The default values are loaded if the data is not found
            and then the handlers for the commands are set.
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
            self.local_db = try_convert(self.save_data.get("local_db"), bool)

            # Load the default values if the data is not found
            self.load_defaults()

            # Load the handlers
            self.handlers = [self.command_help, self.command_logs, self.command_errors, self.command_server,
                             self.command_database]

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
            """
            Logs a debug message of the given type with the current time to the console and the session logs. If
            the log type is in the log_ignore list it will not be logged
            @param message: The text to be displayed in the log
            @param log_type: The type of log this message is, this is used to determine the if the log should be ignored
            @return: None, this function does not return anything
            """

            # Import colour
            from Maxs_Modules.renderer import Colour

            # Check if the log type is ignored
            if log_type in self.log_ignore:
                return

            # Get the time
            time_now = datetime.now().strftime("%H:%M:%S")

            # Print the message
            print(f"{Colour.warning}[{time_now}]{Colour.BOLD}[{log_type}]{Colour.RESET} {message}")

            # Add the message to the session logs
            session_message_log.append(f"[{time_now}][{log_type}] {message}")

        def command_database(self, *args: tuple) -> None:
            """
            Handles the database command. This will be updated in the future when the local database is implemented
            @param args: A tuple of arguments to be passed to the handler, to get a list of viable arguments use -h
            """
            from Maxs_Modules.renderer import render_text

            # If there is no arguments, add the help argument as the default
            if len(args) == 0:
                args = ["-h"]

            # Loop through the arguments
            for arg in args:

                # Handle the arguments
                match arg:
                    case "-h":
                        render_text("Params:")
                        render_text(" -h: Shows this help message")
                        render_text(" -store: Store the API data in a local database?")
                        render_text(" -use: Use the local database?")
                        render_text(" -clear: Clear the local database?")

        def command_server(self, *args: tuple) -> None:
            """
            Handles the server command. Currently only supports -h, -ip.
            @param args: A tuple of arguments to be passed to the handler, to get a list of viable arguments use -h
            """
            from Maxs_Modules.network import get_ip
            from Maxs_Modules.renderer import render_text

            # If there is no arguments, add the help argument as the default
            if len(args) == 0:
                args = ["-h"]

            # Loop through the arguments
            for arg in args:

                # Handle the arguments
                match arg:
                    case "-h":
                        render_text("Params:")
                        render_text(" -h: Shows this help message")
                        render_text(" -ip: Gets this devices ip address")

                    case "-ip":
                        render_text("IP: " + get_ip())

                    case _:
                        render_text("Unknown arg: " + arg)

        def command_help(self, *args: tuple) -> None:
            """
            Prints all the commands, if a command is given as an arg it will run the command with the -h arg
            @param args: The commands to run
            """
            from Maxs_Modules.renderer import render_text

            # Default behaviour for no args
            if len(args) == 0:
                render_text("Some commands may support -h for more info")
                render_text("Commands:")
                for command in self.commands:
                    render_text(" * " + command)

            # Loop through the args
            for arg in args:

                # If the arg is a command, run the command with the -h arg
                if arg in self.commands:
                    self.handlers[self.commands.index(arg)]("-h")
                else:
                    render_text("Unknown command: " + arg)

        def command_logs(self, *args: tuple) -> None:
            """
            Allows the user to view the logs, and change the log settings. The default behaviour is to list the logs
            @param args: The args to pass to the command, to get a list of viable arguments use -h
            """

            # Import the modules
            from Maxs_Modules.tools import get_user_input_of_type, string_bool
            from Maxs_Modules.renderer import Colour, menu_manager, render_text

            # Default behaviour for no args
            if len(args) == 0:
                args = ["-list"]

            # Loop through each arg handling it
            for arg in args:
                match arg:
                    case "-h":
                        render_text("Params:")
                        render_text(" -h: Shows this help message")
                        render_text(" -ignore-add: Adds a log type to ignore")
                        render_text(" -ignore-remove: Removes a log type to ignore")
                        render_text(" -ignore-list: Lists the log types to ignore")
                        render_text(" -ignore-clear: Clears the log types to ignore")
                        render_text(" -list: Lists current the logs")
                        render_text(" -list-full: List the full history of logs")
                        render_text(" -clear-history: Clears the full history of logs")
                        render_text(" -store: Sets weather or not to store the logs")
                        render_text(" -store-location: Sets the location to store the logs")
                        render_text(" -store-individual: Sets weather or not to store the logs in individual files")
                        render_text(" -store-max: Sets the maximum amount of logs to store")
                        render_text(" -menu-history: Shows a log of all the menus in the current session")
                        render_text(" -menu-history-input: Shows a log of all the input in the menus in the current session")

                    case "-ignore-add":
                        self.log_ignore.append(get_user_input_of_type(str, "Log type to ignore: "))

                    case "-ignore-remove":
                        # Remove the log type from the ignore list
                        try:
                            self.log_ignore.pop(
                                self.log_ignore.index(get_user_input_of_type(str, "Log type to remove: ")))
                        except ValueError:
                            render_text("Log type not found")

                    case "-ignore-list":
                        render_text("Log types to ignore:")
                        for log_type in self.log_ignore:
                            render_text(" - " + log_type)

                    case "-ignore-clear":
                        self.log_ignore = []

                    case "-list":
                        render_text("Current logs:")
                        for log in session_message_log:
                            render_text(" - " + log)

                    case "-list-full":
                        render_text("Full logs:")
                        for log in self.full_message_log:
                            render_text(" - " + str(log))

                    case "-store":
                        self.store_logs = get_user_input_of_type(string_bool, "Store the logs on file? (True/False)")
                    case "-store-location":
                        self.save_logs_location = get_user_input_of_type(str, "Location to store the logs: ")

                    case "-store-individual":
                        self.individual_log_files = get_user_input_of_type(string_bool,
                                                                           "Store the logs in individual files? (True/False)")

                    case "-store-max":
                        self.max_log_history = get_user_input_of_type(int, "Maximum amount of logs to store: ")

                    case "-clear-history":
                        self.full_message_log = []

                    case "-menu-history":
                        for menu in menu_manager.menu_history_names:
                            render_text("- " + str(menu))

                    case "-menu-history-input":
                        for user_input in menu_manager.menu_history_input:
                            render_text("- " + str(user_input))

                    case _:
                        render_text("Unknown command: " + arg)

        def command_errors(self, *args: tuple) -> None:
            """
            Allows the user to view/clear the errors (note: errors made by the error() funct, not the runtime errors)
            @param args: The args to pass to the command, if none are given it will show the help message
            """
            from Maxs_Modules.renderer import render_text

            # Default behaviour for no args
            if len(args) == 0:
                args = ["-h"]

            # Loop through each arg handling it
            for arg in args:
                match arg:
                    case "-h":
                        render_text("Params:")
                        render_text(" -h: Shows this help message")
                        render_text(" -list: Lists current the errors")
                        render_text(" -list-full: List the full history of errors")
                        render_text(" -clear-history: Clears the past errors")

                    case "-list":
                        render_text("Current errors:")
                        for log_error in session_error_log:
                            render_text(" - " + log_error)

                    case "-list-full":
                        render_text("Full errors:")
                        for log_error in self.full_error_log:
                            render_text(" - " + str(log_error))

                    case "-clear-history":
                        self.full_error_log = []

                    case _:
                        render_text("Unknown command: " + arg)

        def handle(self, user_input: list) -> None:
            """
            Attempts to run the handler for the command, and passes the args to the handler (as a tuple)
            @param user_input: The commands and args to pass to the handler
            """

            # Get the first word of the command
            command = user_input[0]

            # Get the reset of the words as the args
            args = user_input[1:]

            if command in self.commands:
                # Run the handler for the command and pass the args
                self.handlers[self.commands.index(command)](*args)

        def save(self) -> None:
            """
            Save the debug data to the save file via the SaveFile.save() function
            """
            self.save_data = self.__dict__
            self.save_data.pop("handlers")

            super().save()

        def close_debug_session(self):
            """
            Closes the debug session, saving the logs if needed either to their individual files or the main debug file
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
                    with open(str(self.save_logs_location) + log_name, "w") as file:
                        file.write("Message log:\n"
                                   + str(session_message_log)
                                   + "\n\nError log:\n"
                                   + str(session_error_log))

                else:
                    # Check if the logs are full and if so remove the oldest log
                    if len(self.full_message_log) > self.max_log_history:
                        self.full_message_log.pop(0)
                    if len(self.full_error_log) > self.max_log_history:
                        self.full_error_log.pop(0)

                    # Add the session logs to the full logs
                    self.full_message_log.append(session_message_log)
                    self.full_error_log.append(session_error_log)

            self.save()

    # Set the debugger to the debug class
    maxs_debugger = Debug()


# - - - - - - - Functions - - - - - - -#

def close_debug_session() -> None:
    """
    Run the close_debug_session() function of the debugger, if it is initialized
    """
    # Only run if the debugger is initialized
    if maxs_debugger is not None:
        maxs_debugger.close_debug_session()


def debug_cli(command: list) -> None:
    """
    If the debugger is initialized and debug is enabled, handle the command passed
    @param command: The command to handle and args to pass to the handler (as a list)
    """
    # Only run if the debugger is initialized
    if maxs_debugger is not None:
        maxs_debugger.handle(command)


def debug_message(message: str, log_type: str = "info") -> None:
    """
    If the debugger is initialized and debug is enabled, print a debug message via the log() function of the debugger
    class
    @param message: The debug message to print
    @param log_type: The type of log to print
    """
    # Only run if the debugger is initialized
    if maxs_debugger is not None:
        maxs_debugger.log(message, log_type)


def error(error_message: str) -> None:
    """
    Print an error message in red and then wait 2 seconds
    @param error_message: The error message to print
    """
    # Print the coloured error message
    from Maxs_Modules.renderer import render_text
    render_text("ERROR: " + error_message)

    # Add the error to the error log if debug is enabled
    if maxs_debugger is not None:
        session_error_log.append(error_message)

    # Give the user time to read the error message
    time.sleep(2)


def handle_arg(arg: str, get_value: bool = False) -> str or None:
    """
    Handles the args passed to the program and returns the arg if it is found, if get_value is True it will return the
    following argument
    @param arg: The arg to check for
    @param get_value: True if the following argument should be returned, False if not (default: False)
    @return: The arg or value if it is found, None if not
    """
    # Get the args passed to the program
    program_args = sys.argv[1:]

    # Loop through each arg and check if it matches the arg passed
    for index in range(len(program_args)):
        if arg == program_args[index]:

            # If the arg is found, check if the value should be returned
            if get_value:

                # Check if there is a value after this arg
                if index != len(program_args):
                    return program_args[index + 1]
                else:
                    return None

            return arg

    return None

in_ide = (handle_arg("--ide") == "--ide")
use_debug = (handle_arg("--debug") == "--debug")
