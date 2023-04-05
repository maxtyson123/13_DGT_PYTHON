# - - - - - - - Imports - - - - - - -#
import base64
import json
import os
from Maxs_Modules.debug import debug_message, error
from Maxs_Modules.tools import try_convert, set_if_none

# - - - - - - - Variables - - - - - - -#

OFFLINE_QUESTIONS_JSON = "ProgramData/questions.json"
DATA_FOLDER = "UserData/"


# - - - - - - - Functions - - - - - - -#


def load_questions_from_file() -> dict:
    """
    Loads a json array of questions from the offline questions file specified in the offline_questions_file variable.
    This is just a downloaded JSON api response from the Open Trivia Database API.

    @return: JSON object of questions
    """
    # Open the file in read mode
    with open(OFFLINE_QUESTIONS_JSON, "r") as file:
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

        # If the user wants to autoload the file then try to run the load function
        if auto_load:
            debug_message("Auto loading file", "save_file")
            self.load()

    def load(self) -> None:
        """
        Loads the data from the save file into the save_data dictionary. If the file is corrupt or does not exist
        then the save_data dictionary will remain the same as its previous state. The caller of this function needs to
        manually load the variables from the save_data dictionary, it is also good practice to check if the types are
        correct as JSON can be manipulated.

        @return: None, this function will return if the file is corrupt or does not exist
        """
        debug_message("Loading file from " + self.save_file, "save_file")

        # Try to load the data from the save file in read mode, if it fails then warn the user
        try:
            with open(self.save_file, "r") as file:
                debug_message("File opened", "save_file")

                # Decode the data from the file
                data = file.read().encode('utf-8')
                try:
                    data = base64.b64decode(data)
                except base64.binascii.Error:
                    debug_message("File is not base64 encoded, must be an older save", "save_file")

                # Try Load the data from the file and convert it to a dictionary, if it fails then warn the user and
                # close the file then delete the file
                try:
                    self.save_data = json.loads(data.decode('utf-8'))
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
        Saves the data from the save_data dictionary to the save file. If the file does not exist then it will be
        created. The save_data dictionary needs to be set before this function is called, do this by setting the
        save_data dictionary to the __dict__ of the subclass. Note: do not need to remove the save_data dictionary
        from the save_data dictionary as this is done automatically.
        """
        debug_message("Saving file to " + self.save_file, "save_file")

        if not os.path.exists(DATA_FOLDER):
            os.mkdir(DATA_FOLDER)

        # Open the file and dump the object as a dictionary, then close the file
        with open(self.save_file, "w") as file:
            save_dict = self.save_data

            # Try to remove the save_data dictionary from the save data as this causes a loop error when serializing
            try:
                del save_dict["save_data"]
            except KeyError:
                pass

            # Encode and save the data, this makes it harder for the user to edit the file
            data = json.dumps(save_dict, ensure_ascii=False).encode('utf-8')
            data = base64.b64encode(data)
            file.write(data.decode('utf-8'))
            file.close()


class UserData(SaveFile):
    # User settings
    display_mode = None
    network = None
    auto_fix_api = None

    def __init__(self) -> None:
        """
        Create a new UserData object, loaded from setup.json
        """
        super().__init__(DATA_FOLDER + "data.json")

        # Load the data from the save file
        self.display_mode = try_convert(self.save_data.get("display_mode"), str)
        self.network = try_convert(self.save_data.get("network"), bool)
        self.auto_fix_api = try_convert(self.save_data.get("auto_fix_api"), bool)

        # Load the default values if the data is not found
        self.load_defaults()

    def load_defaults(self) -> None:
        """
        Load the default values for the user data if they are not found
        """
        self.display_mode = set_if_none(self.display_mode, "GUI")
        self.network = set_if_none(self.network, True)
        self.auto_fix_api = set_if_none(self.auto_fix_api, True)

    def save(self) -> None:
        """
        Save the user data to the save file
        """
        self.save_data = self.__dict__

        super().save()


