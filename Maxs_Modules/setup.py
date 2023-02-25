# - - - - - - - Imports - - - - - - -#
import os
import subprocess
import sys

from Maxs_Modules.files import SaveFile
from Maxs_Modules.tools import get_user_input_of_type, try_convert, set_if_none, strBool
from Maxs_Modules.debug import debug_message, error
from Maxs_Modules.renderer import Colour

# - - - - - - - Variables - - - - - - -#

data_folder = "UserData/"

# - - - - - - - Classes - - - - - - - -#


class UserData(SaveFile):

    # States
    setup_complete = False

    # User settings
    display_mode = None
    network = None
    auto_fix_api = None

    # Executable settings
    python_exe_command = None
    packages = []
    use_py_env = False
    py_env_pip_path = ""
    py_env_py_path = ""

    def __init__(self) -> None:
        """
        Create a new UserData object, loaded from setup.json
        """
        super().__init__(data_folder+"setup.json")

        # Load the data from the save file
        self.setup_complete = try_convert(self.save_data.get("setup_complete"), bool)
        self.display_mode = try_convert(self.save_data.get("display_mode"), str)
        self.network = try_convert(self.save_data.get("network"), bool)
        self.auto_fix_api = try_convert(self.save_data.get("auto_fix_api"), bool)
        self.python_exe_command = try_convert(self.save_data.get("python_exe_command"), str)
        self.packages = try_convert(self.save_data.get("packages"), list)
        self.use_py_env = try_convert(self.save_data.get("use_py_env"), bool)
        self.py_env_pip_path = try_convert(self.save_data.get("py_env_pip_path"), str)
        self.py_env_py_path = try_convert(self.save_data.get("py_env_py_path"), str)

        # Load the default values if the data is not found
        self.load_defaults()

    def install_package(self, package: str) -> None:
        """
        Install a package using pip. (Built in module pip not pip.exe)
        @param package: The package to install
        """
        install_command = self.python_exe_command + " -m pip install " + package
        os.system(install_command)

    def load_defaults(self) -> None:
        """
        Load the default values for the user data if they are not found
        """
        self.setup_complete = set_if_none(self.setup_complete, False)
        self.display_mode = set_if_none(self.display_mode, "CLI")
        self.network = set_if_none(self.network, False)
        self.auto_fix_api = set_if_none(self.auto_fix_api, True)
        self.python_exe_command = set_if_none(self.python_exe_command, "python")
        self.packages = set_if_none(self.packages, [])
        self.use_py_env = set_if_none(self.use_py_env, False)
        self.py_env_pip_path = set_if_none(self.py_env_pip_path, "")
        self.py_env_py_path = set_if_none(self.py_env_py_path, "")

    def save(self) -> None:
        """
        Save the user data to setup.json
        """
        self.save_data = self.__dict__

        super().save()

    def get_packages(self, package_list: list) -> None:
        """
        Installs a list of packages if they are not already installed
        @param package_list: The list of packages to install
        """
        for package in package_list:

            # Check if the package is not already installed
            if package not in self.packages:
                self.install_package(package)
                self.packages.append(package)
                self.save()

                # Restart the script with the new packages
                subprocess.call(sys.executable + ' "' + os.path.realpath(__file__) + '"')


    def init_script(self) -> None:
        """
        Initialise the script, checking if the setup is complete and if the user is using the python virtual
        environment if they chose to configure the script to use it.
        """
        # Check if the setup is complete
        if not self.setup_complete:
            self.setup()

        if self.use_py_env:

            # Check if the virtual environment exists
            if not os.path.exists("venv"):
                error("The python virtual environment was not found. Please run the setup again.")

                # Remove the setup data
                os.remove(data_folder+"setup.json")

                # Close the script
                exit()

            exec_path = sys.executable
            debug_message(exec_path, "setup")

            # Check if the user has run the script with the python virtual environment (if needed)
            if not exec_path == self.py_env_py_path:

                print("Please run this script from the python virtual environment. Attempting to run now.")
                print("Please wait...")

                # Execute the script from the python virtual environment (main.py)
                os.system(f"{self.py_env_py_path} main.py")
                exit()

    def setup(self) -> None:
        """
        Run the setup wizard, this will ask the user for the settings they want to use and save them to setup.json.
        This is normally called once when the script is first run.
        """
        os.system("cls")
        print("Welcome to the setup wizard")

        # Get the user settings
        self.display_mode = get_user_input_of_type(str, "Please enter the display mode (CLI, GUI): ", ["CLI", "GUI"])
        self.network = get_user_input_of_type(strBool, "Do you want to use the network? ("+Colour.true_or_false_styled()
                                              + "): ")

        print("Note: Fixing the API involves removing parameters from the API call until it goes though, this can fix "
              "errors where there arent enough questions of that type in the database, however it can mean that the "
              "question types arent the same as the ones you selected.")
        self.auto_fix_api = get_user_input_of_type(strBool, "Do you want to auto fix the API if an error occurs? "
                                                            "(" + Colour.true_or_false_styled() + "): ")

        # Get the python executable command
        self.python_exe_command = sys.executable

        # Check if the user wants to use a python virtual environment
        print("Note a python virtual environment can be buggy on WBHS computers and/or other admin restricted and is "
              "only recommended as a work around for certain users.")
        self.use_py_env = get_user_input_of_type(strBool, "Do you want to use a python virtual environment? "
                                                          "(" + Colour.true_or_false_styled() + "): ")

        # User has now completed the setup
        self.setup_complete = True

        self.save()
