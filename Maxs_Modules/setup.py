# - - - - - - - Imports - - - - - - -#
import os
import sys

from Maxs_Modules.files import SaveFile
from Maxs_Modules.tools import get_user_input_of_type, try_convert, set_if_none, strBool, debug, error

# - - - - - - - Variables - - - - - - -#

data_folder = "UserData/"

# - - - - - - - Classes - - - - - - - -#


def install_package(package):
    install_command = "python -m pip install " + package
    os.system(install_command)


class SetupData(SaveFile):
    setup_complete = False
    has_pip = False
    packages = []
    use_py_env = False
    py_env_pip_path = ""
    py_env_py_path = ""

    def __init__(self):
        super().__init__(data_folder+"setup.json")

        # Load the data from the save file
        self.setup_complete = try_convert(self.save_data.get("setup_complete"), bool)
        self.has_pip = try_convert(self.save_data.get("has_pip"), bool)
        self.packages = try_convert(self.save_data.get("packages"), list)
        self.use_py_env = try_convert(self.save_data.get("use_py_env"), bool)
        self.py_env_pip_path = try_convert(self.save_data.get("py_env_pip_path"), str)
        self.py_env_py_path = try_convert(self.save_data.get("py_env_py_path"), str)

        # Load the default values if the data is not found
        self.load_defaults()

    def load_defaults(self):
        self.setup_complete = set_if_none(self.setup_complete, False)
        self.has_pip = set_if_none(self.has_pip, False)
        self.packages = set_if_none(self.packages, [])
        self.use_py_env = set_if_none(self.use_py_env, False)
        self.py_env_pip_path = set_if_none(self.py_env_pip_path, "")
        self.py_env_py_path = set_if_none(self.py_env_py_path, "")

    def save(self):
        self.save_data = self.__dict__

        super().save()

    def get_packages(self, package_list):
        for package in package_list:

            # Check if the package is not already installed
            if package not in self.packages:
                install_package(package)
                self.packages.append(package)

        # Save the list of packages
        self.save()

    def init_script(self):

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
            debug(exec_path, "setup")

            # Check if the user has ran the script with the python virtual environment (if needed)
            if not exec_path == self.py_env_py_path:

                print("Please run this script from the python virtual environment. Attempting to run now.")
                print("Please wait...")

                # Execute the script from the python virtual environment (main.py)
                os.system(f"{self.py_env_py_path} main.py")
                exit()

    def setup(self):
        # Will remove later due to PIP is now installed by default

        os.system("cls")
        print("Welcome to the setup wizard")
        os.system("python -m pip --version")

        # User has now completed the setup
        self.setup_complete = True

        self.save()
