# - - - - - - - Imports - - - - - - -#
import json
import os
from Maxs_Modules.debug import debug_message, error

# - - - - - - - Variables - - - - - - -#

offline_questions_file = "ProgramData/questions.json"

# - - - - - - - Functions - - - - - - -#


def load_questions_from_file() -> dict:
    """
    Loads a json array of questions from the offline questions file specified in the offline_questions_file variable.
    This is just a downloaded JSON api response from the Open Trivia Database API.

    @return: JSON array of questions
    """
    # Open the file in read mode
    with open(offline_questions_file, "r") as file:

        # Read the file into a json object
        questions = json.load(file)

        # Return the questions
        return questions["results"]

# - - - - - - - Classes - - - - - - -#


class SaveFile:
    save_file = "save.json"
    save_data = {}

    def __init__(self, save_file: str, auto_load: bool = True) -> None:
        """
        Initialises the save file class

        @param save_file: The file to save the data to, will be created if it does not exist
        @param auto_load: If the file should be loaded automatically when the class is initialised,
        by default this is True
        """
        self.save_file = save_file

        # If the user wants to autoload the file then try run the load function
        if auto_load:
            debug_message("Auto loading file", "save_file")
            self.load()

    def load(self) -> None:
        """
        Loads the data from the save file into the save_data dictionary
        @return: None, this function will return if the file is corrupt or does not exist
        """
        debug_message("Loading file from " + self.save_file, "save_file")

        # Try to load the data from the save file in read mode, if it fails then warn the user
        try:
            with open(self.save_file, "r") as file:
                debug_message("File opened", "save_file")

                # Try Load the data from the file and convert it to a dictionary, if it fails then warn the user and
                # close the file then delete the file
                try:
                    self.save_data = json.load(file)
                except json.decoder.JSONDecodeError:
                    error("File is corrupt, deleting file automatically")
                    file.close()
                    os.remove(self.save_file)
                    return

                # Note: the subclass has to load the data from the save_data dictionary as there is no way for the
                # super class to interact with the subclass

                # Close the file
                file.close()

        except FileNotFoundError:
            debug_message("File not found", "save_file")
            return

    def save(self) -> None:
        """
        Saves the data from the save_data dictionary to the save file
        """
        debug_message("Saving file to " + self.save_file, "save_file")

        # Open the file and dump the object as a dictionary, then close the file
        with open(self.save_file, "w") as file:
            save_dict = self.save_data

            # Try to remove the save_data dictionary from the save data as this causes a loop error when serializing
            try:
                del save_dict["save_data"]
            except KeyError:
                print("KeyError: save_data")

            json.dump(save_dict, file)
            file.close()
