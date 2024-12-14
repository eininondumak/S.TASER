#! /usr/bin/env python
# -*- coding: utf-8 -*-

# folder_selector.py

import tkinter as tk
from tkinter import filedialog
import json


def select_folder():
    """
    Opens a folder selection dialog and prints the selected folder's path in JSON format.

    This function uses Tkinter to display a folder selection dialog box. The selected folder's
    path is captured and printed in JSON format for structured use in other applications.

    Returns:
        None
    """
    # Initialize the root Tkinter window
    root = tk.Tk()
    
    # Bring the window to the foreground and hide it
    root.attributes("-topmost", True)
    root.withdraw()  # Hide the root window to only show the folder dialog
    
    # Open the folder selection dialog
    folder_path = filedialog.askdirectory()  # Allow user to select a folder
    
    # If a folder is selected, print its path in JSON format
    if folder_path:
        print(json.dumps({"folder_path": folder_path}))
    
    # Destroy the root window after use
    root.destroy()


# Main entry point of the script
if __name__ == "__main__":
    select_folder()
