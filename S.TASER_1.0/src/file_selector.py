#! /usr/bin/env python
# -*- coding: utf-8 -*-

# file_selector.py

import tkinter as tk
from tkinter import filedialog
import json


def select_file():
    """
    Opens a file dialog for the user to select a file and prints the file path as JSON.

    This function uses Tkinter to display a file selection dialog box. The selected file's
    path is returned in a JSON format.

    Returns:
        None
    """
    # Initialize a Tkinter root window
    root = tk.Tk()
    
    # Make the root window always on top and hide it
    root.attributes("-topmost", True)
    root.withdraw()  # Hide the root window to only show the file dialog
    
    # Open a file selection dialog
    file_path = filedialog.askopenfile(filetypes=(("All files", "*.*"),))  # Allow selection of all file types
    
    # If a file is selected, print its path in JSON format
    if file_path:
        print(json.dumps({"file_path": file_path.name}))
    
    # Destroy the root window after use
    root.destroy()


# If this script is run as the main program, invoke the select_file function
if __name__ == "__main__":
    select_file()
