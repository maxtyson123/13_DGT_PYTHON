# - - - - - - - Imports - - - - - - -#
from Maxs_Modules.setup import UserData
from Maxs_Modules.tools import error, debug

# Get the setup data
setup = UserData()
setup.get_packages(["requests"])

import requests

# - - - - - - - Functions - - - - - - -#


def api_get_questions(amount, category, difficulty, type):
    # Create the URL
    url = f"https://opentdb.com/api.php?amount={amount}"

    # Ignore the options if they are "Any" (or none because 'convert_question_settings_to_api()' already does this)
    # since the API gives any by default
    if category is not None:
        url += f"&category={category}"

    if type is not None:
        url += f"&type={type}"

    if difficulty != "Any":
        url += f"&difficulty={difficulty.lower()}"

    debug(url, "API")

    # Get the questions from the API
    response = requests.get(url)

    # Check if the was any errors
    if response.status_code != 200:
        error("Failed to get questions from the API")
        return

    # Debug
    debug(str(response.json()), "API")

    # Check for errors
    match response.json()["response_code"]:
        case 0:
            pass # No errors, just good to have a defined case so that I don't forget it
        case 1:
            error("No results found")
        case 2:
            error("Invalid parameter")



    # Return the questions
    return response.json()["results"]
