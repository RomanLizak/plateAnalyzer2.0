import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import os
import psutil

from plateAnalyzer import PlateAnalyzer

class NotepadApp:
    plus_tab_label = "   +   "

    def __init__(self, root):
        self.root = root
        self.root.title("Plate Analyzer 2.0")
        self.root.iconbitmap('logo.ico')
        
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both')

        self.add_plus_tab()
        
        self.notebook.bind("<Button-1>", self.on_tab_click)
        self.notebook.bind("<Button-3>", self.on_tab_right_click)

        self.create_menu(root)

        #dictionary to keep track of tabs - names : object
        #object holds information about its name and stores all data
        self.tabs = {}
        self.selected_object = None

    def on_frame_configure(self,canvas):
        canvas.configure(scrollregion=canvas.bbox("all"))

    def enable_scrolling(self, canvas, event=None):
        #get the position of the most bottom most right frame
        #get the maximum values of all the frames
        max_x = max(self.selected_object.frames['frame_plate_info'].winfo_x(),
                    self.selected_object.frames['frame_job_info'].winfo_x(),
                    self.selected_object.frames['frame_preview'].winfo_x() + self.selected_object.frames['frame_preview'].winfo_width() + 20)

        max_y = max(self.selected_object.frames['frame_plate_info'].winfo_y(),
                    self.selected_object.frames['frame_job_info'].winfo_y(),
                    self.selected_object.frames['frame_ax_settings'].winfo_y() + self.selected_object.frames['frame_ax_settings'].winfo_height() + 20)
        
        # Bind the scroll 
        if canvas.winfo_width() >= max_x:#self.notebook.winfo_width():
            canvas.unbind_all("<Shift-MouseWheel>")
        else:
            canvas.bind_all("<Shift-MouseWheel>", lambda e: canvas.xview_scroll(int(-1 * (e.delta / 120)),"units"))

        if canvas.winfo_height() >= max_y:#self.notebook.winfo_height():
            canvas.unbind_all("<MouseWheel>")
        else:
            canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)),"units"))

    def disable_scrolling(self, canvas, event=None):
        # Unbind the scroll events
        canvas.unbind_all("<MouseWheel>")
        canvas.unbind_all("<Shift-MouseWheel>")

    def add_tab(self,event=None):
        # add open file dialog
        file_path = filedialog.askopenfilename()
        
        if file_path:
            # delete the suffix from the file path and save the rest to self.title
            #title = '  ' + os.path.splitext(os.path.basename(file_path))[0] + '  '
            
            object = PlateAnalyzer(file_path)
            self.selected_object = object
            self.tabs[object.name] = object
            title = '  ' + object.name + '  '

            # create a frame for the new tab
            frame_main = tk.Frame(self.notebook)
            self.notebook.insert(len(self.notebook.tabs()) - 1, frame_main, text=title)
            object.frames['frame_root'] = frame_main

            # Create a Canvas widget
            canvas = Canvas(frame_main) 
            canvas.pack(side=LEFT, fill=BOTH, expand=True)
            self.canvas_main = canvas
            
            # Create a Frame to hold all the other frames
            container = Frame(canvas)
            canvas.create_window((0, 0), window=container, anchor=NW)
            canvas.bind("<Enter>", lambda event: self.enable_scrolling(canvas))
            canvas.bind("<Leave>", lambda event: self.disable_scrolling(canvas)) 
            
            # Bind the frame configure event to update the scroll region
            container.bind("<Configure>", lambda event: self.on_frame_configure(canvas))

            # Add a vertical Scrollbar widget
            v_scrollbar = Scrollbar(canvas, orient=VERTICAL, command=canvas.yview)
            v_scrollbar.pack(side=RIGHT, fill=Y)
            canvas.configure(yscrollcommand=v_scrollbar.set)

            # Add a horizontal Scrollbar widget
            h_scrollbar = Scrollbar(canvas, orient=HORIZONTAL, command=canvas.xview)
            h_scrollbar.pack(side=BOTTOM, fill=X)
            canvas.configure(xscrollcommand=h_scrollbar.set)

            # Configure the Canvas to work with the Scrollbars
            canvas.config(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)


            # Add frames to the tab
            self.add_frame_plate_info(object,container)
            self.add_frame_job_info(object,container)
            self.add_frame_data_selection(object,container)
            self.add_frame_figure_selection(object,container)
            self.add_frame_ax_settings(object,container)
            self.add_frame_preview(object,container)
            self.add_frame_template(object,container)

                                       
    def add_frame_plate_info(self, object, parent_frame):
        #create a frame for the plate info
        frame_plate_info = LabelFrame(parent_frame, text="Plate Info", width=475, height=200)
        frame_plate_info.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky='nws')
        frame_plate_info.grid_propagate(flag=False)
        object.frames['frame_plate_info'] = frame_plate_info

        row_idx, col_idx = 0, 0
        #fill the frame with data - plate info
        for item in object.df_plate:
            name, value = item
            Label(frame_plate_info, text=name).grid(row=row_idx, column=col_idx, sticky='w', padx=5, pady=2)
            Label(frame_plate_info, text=value).grid(row=row_idx, column=col_idx+1, sticky='w', padx=5, pady=2)
            row_idx = row_idx + 1
            if row_idx > 7:
                row_idx = 0
                col_idx = 2

        # force update to ensure the tab is fully rendered
        self.root.update_idletasks()
            
    def add_frame_job_info(self, object, parent_frame):
        frame_job_info = LabelFrame(parent_frame, text="Job Info")
        frame_job_info.grid(row=0, column=2, columnspan=2, padx=10, pady=10, sticky='news')
        #frame_job_info.grid_propagate(flag=False)
        object.frames['frame_job_info'] = frame_job_info

        #get height of the frame_plate_info and create a canvas
        height_frame_plate_info = object.frames['frame_plate_info'].winfo_height()
        canvas = Canvas(frame_job_info, width=625, height=height_frame_plate_info-20)
        canvas.grid(row=1, column=0, sticky='news')
        self.canvas_job_info = canvas

        
        #add vertical scrollbar for the frame_job_info, scrollable if it is bigger than frame_plate_info
        scrollbar = Scrollbar(frame_job_info, orient="vertical")
        scrollbar.grid(row=1, column=1, sticky='ns')

        


        scrollbar.config(command=canvas.yview)
        canvas.config(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Enter>", lambda event: canvas.bind_all("<MouseWheel>",
                                                         lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)),
                                                                                       "units")))
    
        canvas.bind("<Leave>", lambda event: canvas.unbind_all("<MouseWheel>"))
        canvas.bind("<Leave>",lambda event: self.enable_scrolling(self.canvas_main))

        container = Frame(canvas)
        canvas.create_window((0, 0), window=container, anchor=NW)

        help_frame = Frame(frame_job_info)
        help_frame.grid(row=0, column=0, sticky='news')
        # add header
        for col_idx, item in enumerate(object.df_job[0]):
           Label(help_frame, text=item).grid(row=0, column=col_idx, sticky='', padx=5, pady=2)
        
        col_widths = []
        for col_idx in range(len(object.df_job[0])):
            col_widths.append(len(object.df_job[0][col_idx])-2)


        # fill the frame with data - job info
        for row_idx, row in enumerate(object.df_job[1:]):
            for col_idx, item in enumerate(row):
                Label(container, text=item, width=col_widths[col_idx]).grid(row=row_idx, column=col_idx, sticky='', padx=5, pady=2)
                #Label(container, text=item).grid(row=row_idx, column=col_idx, sticky='', padx=5, pady=2)
                

        # force update to ensure the tab is fully rendered
        self.root.update_idletasks()

    def add_frame_data_selection(self, object, parent_frame):
        frame_data_selection = LabelFrame(parent_frame, text="Data slection")
        frame_data_selection.grid(row=1, column=0, columnspan=2, rowspan=6, padx=10, pady=10, sticky='nws')
        #frame_job_info.grid_propagate(flag=False)
        object.frames['frame_data_selection'] = frame_data_selection
        

        #get height of the screen and adjust height to fill the screen minus height of plate_frame_info minus some padding
        available_height = self.root.winfo_screenheight() - object.frames['frame_plate_info'].winfo_height()-195
        #get height of the screen - height of the head of the window - height of the menu - height of the windows start bar
        canvas = Canvas(frame_data_selection, width=200, height=available_height)
        canvas.grid(row=0, column=0, sticky='news')
        self.canvas_data_selection = canvas

        #add vertical scrollbar for the frame_job_info, scrollable if it is bigger than frame_plate_info
        scrollbar = Scrollbar(frame_data_selection, orient="vertical")
        scrollbar.grid(row=0, column=1, sticky='ns')
        scrollbar.config(command=canvas.yview)
        canvas.config(yscrollcommand=scrollbar.set)
        
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        # when enter the canvas, mouse scrolling is enabled
        canvas.bind("<Enter>", lambda event: canvas.bind_all("<MouseWheel>",
                                                         lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)),
                                                                                       "units")))  
        # when leave the canvas, mouse scrolling is disabled in frame_data_selection and enabled in frame_main
        canvas.bind("<Leave>", lambda event: canvas.unbind_all("<MouseWheel>"))
        canvas.bind("<Leave>",lambda event: self.enable_scrolling(self.canvas_main))
        
        

        container = Frame(canvas)
        canvas.create_window((0, 0), window=container, anchor=NW)
        #right click will uncheck all checkboxes
        
        
        #create a one column of checkboxes from df_data.columns
        checkbox_idx = 0
        for col in object.df_data.columns:
            checkbox = Checkbutton(container, text=col)
            checkbox.grid(row=checkbox_idx, column=0, sticky='w', padx=5, pady=2)
            checkbox_idx += 1

        self.bind_to_widget_and_children(canvas, "<Button-3>", lambda event: self.uncheck_all(container))
        self.root.update_idletasks()

    def bind_to_widget_and_children(self,widget, event, handler):
            widget.bind(event, handler)
            for child in widget.winfo_children():
                self.bind_to_widget_and_children(child, event, handler)

        
    def uncheck_all(self, container, event=None):
        for child in container.winfo_children():
            child.deselect()

    def add_frame_figure_selection(self, object, parent_frame):
        frame_figure_selection = (LabelFrame(parent_frame, text='Figures', height=150, width=500))
        frame_figure_selection.grid(row=1, column=3, sticky='nwe', padx=10, pady=10)
        frame_figure_selection.grid_propagate(flag=False)
        frame_figure_selection.grid_rowconfigure([0,1,2,3,4,5,6], minsize=21)
        frame_figure_selection.grid_columnconfigure([0,1,2,3,4], minsize=100)
        object.frames['frame_figure_selection'] = frame_figure_selection

        self.root.update_idletasks()

    def get_memory_usage(self):
        
        process = psutil.Process(os.getpid())
        print(f"Memory usage: {process.memory_info().rss / 1024 / 1024} MB") # in bytes process.memory_info().rss / 1024 / 1024
    
    def add_frame_ax_settings(self, object, parent_frame):
        frame_ax_settings = LabelFrame(parent_frame, text='Plot settings', height=350, width=500)
        frame_ax_settings.grid(row=2, column=2, columnspan=2, rowspan=5, pady=20, padx=10, sticky='news')
        frame_ax_settings.grid_propagate(flag=False)
        frame_ax_settings.grid_rowconfigure(0, weight=1)
        frame_ax_settings.grid_columnconfigure(0, weight=1)
        object.frames['frame_ax_settings'] = frame_ax_settings

        
        self.root.update_idletasks()

    def add_frame_preview(self, object, parent_frame):
        frame_preview = LabelFrame(parent_frame, text='Preview', height=375, width=500)
        frame_preview.grid(row=1, column=4, columnspan=2, rowspan=6, sticky='nw', padx=10, pady=10)
        frame_preview.grid_propagate(flag=False)
        object.frames['frame_preview'] = frame_preview

        self.root.update_idletasks()

    def add_frame_template(self, object, parent_frame):
        frame_template = LabelFrame(parent_frame, text='Template', height=150, width=200)
        frame_template.grid(row=0, column=4, sticky='news', pady=10, padx=10)
        object.frames['frame_template'] = frame_template

        self.root.update_idletasks()

    #add the first tab to the notebook
    def add_plus_tab(self):
        frame = tk.Frame(self.notebook)
        self.notebook.add(frame, text=self.plus_tab_label)

    def on_tab_right_click(self, event=None):
        try:
            tab_id = self.notebook.index(f"@{event.x},{event.y}")
            print('right_click ',type(tab_id), tab_id)
        except tk.TclError:
            return
               
        #check if the tab is equal to + sign
        tab_text = self.notebook.tab(tab_id, option="text")

        if tab_text != self.plus_tab_label:
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
        
        # Get the widget name associated with the tab index
        tab_widget_name = self.notebook.tabs()[tab_index]
        frame = self.notebook.nametowidget(tab_widget_name)
    
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
        self.get_memory_usage()


    def exit_app(self,event=None):
        self.root.destroy()
