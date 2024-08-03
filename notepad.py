import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import os

class NotepadApp:
    plus_tab_label = "   +   "

    def __init__(self, root):
        self.root = root
        self.root.title("Plate Analyzer 2.0")

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=1, fill='both')
        
        self.add_plus_tab()
        
        self.notebook.bind("<Button-1>", self.on_tab_click)
        self.notebook.bind("<Button-3>", self.on_tab_right_click)

        self.create_menu(root)

        #dictionary to keep track of tabs - names : object
        #object holds information about its name and stores all data
        self.tabs = {}

    def add_tab(self):
        # add open file dialog
        file_path = filedialog.askopenfilename()
        
        if file_path:
            # delete the suffix from the file path and save the rest to self.title
            title = '  ' + os.path.splitext(os.path.basename(file_path))[0] + '  '
            
            # create a frame for the new tab
            frame_root = tk.Frame(self.notebook)
            self.notebook.insert(len(self.notebook.tabs()) - 1, frame_root, text=title)

            # add a text widget or other content to the tab frame
            frame_main = tk.LabelFrame(frame_root, text="Text", padx=10, pady=10)
            frame_main.pack()

            # force update to ensure the tab is fully rendered
            self.root.update_idletasks()
                        
            

    def add_plus_tab(self):
        frame = tk.Frame(self.notebook)
        self.notebook.add(frame, text=self.plus_tab_label)

    def create_tab_label(self, tab_id, title):
        # Create a frame to hold text and close button
        tab_frame = tk.Frame(self.notebook)
        tab_label = tk.Label(tab_frame, text=title, bg='lightgrey', padx=10)
        tab_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Update the tab with the new frame
        self.notebook.tab(tab_id, text="", image="", compound="none")  # Remove old text/image
        self.notebook.tab(tab_id, text=title)

    def on_tab_right_click(self, event):
        try:
            tab_id = self.notebook.index(f"@{event.x},{event.y}")
        except tk.TclError:
            return

        tab_text = self.notebook.tab(tab_id, option="text")

        if tab_text != self.plus_tab_label:
            tab_id = self.notebook.index(f"@{event.x},{event.y}")
            self.close_tab(tab_id)

    def on_tab_click(self, event):
        try:
            tab_id = self.notebook.index(f"@{event.x},{event.y}")
        except tk.TclError:
            return

        tab_text = self.notebook.tab(tab_id, option="text")

        if tab_text == self.plus_tab_label:
            self.add_tab()
            self.notebook.select(len(self.notebook.tabs()) - 2)

    def close_tab(self, tab_id):
        self.notebook.forget(tab_id)

        del self.tabs[self.tabs[::][0] == self.notebook.tab(tab_id, option="text")]
        

    def create_menu(self, root):
        # Create a menu
        menu_bar = Menu(root)

        # Create a submenu Menu
        file_menu = Menu(menu_bar, tearoff=False)
        file_menu.add_command(label="Open...", accelerator="            Ctrl + O", command=None)
        file_menu.add_command(label="Save", accelerator="            Ctrl + S", command=None)
        file_menu.add_command(label="Save as...", accelerator="Ctrl + Shift + S", command=None)
        file_menu.add_separator()
        file_menu.add_command(label="Close this tab", command=None)
        file_menu.add_command(label="Close all tabs", accelerator="            Ctrl + Q", command=None)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", accelerator="            Ctrl + E", command=None)

        #Create a submenu Help
        help_menu = Menu(menu_bar, tearoff=False)
        help_menu.add_command(label="About...", command=None)

        # Add the submenu to the menu
        menu_bar.add_cascade(label="Menu", menu=file_menu)
        menu_bar.add_cascade(label="Help", menu=help_menu)


        # Configure the window to use the menu
        root.config(menu=menu_bar)

