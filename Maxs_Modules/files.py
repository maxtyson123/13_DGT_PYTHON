# - - - - - - - Imports - - - - - - -#
import json
from Maxs_Modules.tools import debug, error

# - - - - - - - Classes - - - - - - -#


class SaveFile:
    save_file = "save.json"
    save_data = {}

    def __init__(self, save_file, auto_load=True):
        self.save_file = save_file

        # If the user wants to autoload the file then try run the load function
        if auto_load:
            debug("Auto loading file", "save_file")
            self.load()

    def load(self):
        debug("Loading file from " + self.save_file, "save_file")

        # Try to load the data from the save file in read mode, if it fails then warn the user
        try:
            with open(self.save_file, "r") as file:
                debug("File opened", "save_file")

                # Try Load the data from the file and convert it to a dictionary, if it fails then warn the user and
                # close the file then delete the file
                try:
                    self.save_data = json.load(file)
                except json.decoder.JSONDecodeError:
                    error("File is corrupt, deleting file automatically")
                    file.close()
                    os.remove(self.save_file)
                    return

                debug(str(self.save_data), "save_file")

                # Note: the subclass has to load the data from the save_data dictionary as there is no way for the
                # super class to interact with the subclass

                # Close the file
                file.close()

        except FileNotFoundError:
            error("File not found")

    def save(self):
        debug("Saving file to " + self.save_file, "save_file")

        # Open the file and dump the object as a dictionary, then close the file
        with open(self.save_file, "w") as file:
            save_dict = self.save_data

            # Try to remove the save_data dictionary from the save data as this causes an loop error when serializing
            try:
                del save_dict["save_data"]
            except KeyError:
                print("KeyError: save_data")

            debug("File data: " + str(save_dict), "save_file")

            json.dump(save_dict, file)
            file.close()
