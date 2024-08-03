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

    def add_tab(self,event=None):
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
                              
            
    #add the first tab to the notebook
    def add_plus_tab(self):
        frame = tk.Frame(self.notebook)
        self.notebook.add(frame, text=self.plus_tab_label)

    def on_tab_right_click(self, event=None):
        try:
            tab_id = self.notebook.index(f"@{event.x},{event.y}")
        except tk.TclError:
            return
        
        #check if the tab is equal to + sign
        tab_text = self.notebook.tab(tab_id, option="text")

        if tab_text != self.plus_tab_label:
            tab_id = self.notebook.index(f"@{event.x},{event.y}")
            self.close_tab(tab_id)

    def on_tab_click(self, event):
        try:
            tab_id = self.notebook.index(f"@{event.x},{event.y}")
        except tk.TclError:
            return

        #check if the tab is equal to + sign
        tab_text = self.notebook.tab(tab_id, option="text")

        if tab_text == self.plus_tab_label:
            self.add_tab()
            self.notebook.select(len(self.notebook.tabs()) - 2)

    def close_tab(self, tab_id):
        tab_index = self.notebook.index(tab_id)
        frame = self.notebook.nametowidget(tab_id)
        frame.destroy()

        #never select '+' tab
        if int(tab_index) > 0:
            self.notebook.select(tab_index-1)
        
    def close_all_tabs(self,event=None):
        for tab in self.notebook.tabs():
            self.close_this_tab(tab)

    def create_menu(self, root):
        # Create a menu
        menu_bar = Menu(root)

        # Create a submenu Menu
        file_menu = Menu(menu_bar, tearoff=False)
        file_menu.add_command(label="Open...", accelerator="            Ctrl + O", command=self.add_tab)
        file_menu.add_command(label="Save", accelerator="            Ctrl + S", command=self.save)
        file_menu.add_command(label="Save as...", accelerator="            Ctrl + Shift + S", command=self.save_as)
        file_menu.add_separator()
        file_menu.add_command(label="Close this tab", accelerator="            Ctrl + Q",command=self.on_tab_right_click)
        file_menu.add_command(label="Close all tabs", accelerator="            Ctrl + Shift + Q", command=self.close_all_tabs)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", accelerator="            Ctrl + E", command=self.exit_app)

        #Create a submenu Help
        help_menu = Menu(menu_bar, tearoff=False)
        help_menu.add_command(label="Help", accelerator="Ctrl + H", command=self.get_help)

        # Add the submenu to the menu
        menu_bar.add_cascade(label="Menu", menu=file_menu)
        menu_bar.add_cascade(label="Help", menu=help_menu)


        # Configure the window to use the menu
        root.config(menu=menu_bar)

        self.root.bind('<Control-o>', self.add_tab)
        self.root.bind('<Control-s>', self.save)
        self.root.bind('<Control-Shift-S>', self.save_as)
        self.root.bind('<Control-q>', self.close_this_tab)
        self.root.bind('<Control-Shift-Q>', self.close_all_tabs)
        self.root.bind('<Control-e>', self.exit_app)
        self.root.bind('<Control-h>', self.get_help)
        
    def close_this_tab(self, event=None):
        tab_id = self.notebook.select()
        tab_text = self.notebook.tab(tab_id, option="text")
        if tab_text != self.plus_tab_label:
            self.close_tab(tab_id)

    def save(self, event=None):
        print('Save')
    
    def save_as(self, event=None):
        print('Save as')
    
    def get_help(self,event=None):
        print('help')


    def exit_app(self,event=None):
        self.root.destroy()
