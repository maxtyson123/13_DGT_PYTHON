# - - - - - - - Imports - - - - - - -#
from Maxs_Modules.setup import SetupData

# Get the setup data
setup = SetupData()
setup.get_packages(["requests"])

import requests


# - - - - - - - Functions - - - - - - -#

def api_get_questions(amount, category, difficulty, type):
    url = f"https://opentdb.com/api.php?amount={amount}&category={category}&difficulty={difficulty}&type={type}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()