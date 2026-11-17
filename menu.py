"""
-----------------------------------------------------------------------
ASSIGNMENT 14A: Object practice
-----------------------------------------------------------------------
[ ] 1. Header Docstring included.
[ ] 2. Define a class for a part of your project using PascalCase.
[ ] 3. Use __init__ to set private attributes (__variable).
[ ] 4. Write Setters and Getters for the attributes.
[ ] 5. Write a summary function that returns a formatted description.
[ ] 6. Instantiate two distinct objects and print their summaries.
-----------------------------------------------------------------------
"""


# Will rename this file once I have a better idea of what to call it. For now, this is just a placeholder for the assignment.
# Defining a menu category.
class Menu:
    """A class to represent the menu."""


# Code to read in a whole category of items from the menu file, which will normally be a whole line from the file.
def __init__(self, menu_file):
    """Initialize the Menu class with the menu file.
    :param menu_file: The path to the menu file."""
    self.__menu_file = menu_file
    self.__menu = {}


def read_menu(self):
    """Read each category and its details from the menu configuration file."""
    # menu = {}

    try:
        with open(self.__menu_file, "r") as file:
            for line in file:
                try:
                    category, details = line.strip().split(":", 1)
                    self.__menu[category.strip()] = details.strip()
                except ValueError:
                    pass  # This handles lines that don't have the expected format
                except IndexError:
                    pass  # This handles blank lines in the text file

    except FileNotFoundError:
        print(
            f'Could not find "{self.__menu_file}". Please create it or check its name.'
        )
        print("Press enter or any other key to exit.")
    except Exception as e:
        print(e)
