
################ Imports ################
import sys
import os


################ Variables ################
console_width = 30
divider_symbol = "#"
divider = divider_symbol * console_width




################ Functions ################


def validate_user_input_number(input):
   try:
       int(input)      # trys to convert to int
       return True
   except ValueError:  # if it cant the return error
       return False




def menu(menu_title, menu_items):
   # Clear the screen
   os.system("cls")


   # Print the menu
   print(divider)
   text_in_divider(" "+menu_title)
   show_menu(menu_items)


   # Calculate the possible options
   options = [*range(len(menu_items))]




   # Get the user input and validate it
   invalid_input = True
   user_input = "null"
   while invalid_input:
       user_input = input("Choose an option (" + str(options[0]) + "-" + str(options[len(options)-1]) + ") :")
       invalid_input = validate_user_input_number(user_input)


   return user_input






def text_in_divider(item_to_print):
   width_left = console_width - len(item_to_print) - 2  # The length of the text, minus console width, minus 2 for the border
   print(divider_symbol + item_to_print + " " * width_left + divider_symbol)




def show_menu(menu_items):
   print(divider)


   # Loop through all the items in the menu
   for x in range(len(menu_items)):
       item_to_print = " [" + str(x) + "]" + " " + menu_items[x]
       text_in_divider(item_to_print)
   print(divider)




# Main
def main():
   main_menu_items = ["Quit", "Continue"]
   main_menu_title = "Welcome to QUIZ"
   user_input = menu(main_menu_title, main_menu_items)
   print(user_input)


if __name__ == "__main__":
   main()

