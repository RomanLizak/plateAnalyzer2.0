import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import psutil
import gc

from plateAnalyzer import PlateAnalyzer
from myFigure import AddFigure 

class NotepadApp:
    plus_tab_label = "   +   "
    
    def __init__(self, root):
        self.root = root
        self.root.title("Plate Analyzer 2.0")
        self.root.iconbitmap('logo.ico')
        
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both')

        #self.notebook_figures_selection = None

        self.add_plus_tab()
        
        self.notebook.bind("<Button-1>", lambda event: self.on_tab_click('notebook_main', event))
        self.notebook.bind("<Button-3>", lambda event: self.on_tab_right_click('notebook_main', event))

        self.create_menu(root)

        #dictionary to keep track of tabs - names : object
        #object holds information about its name and stores all data
        self.tabs = {}
        self.selected_object_plate = None

    def on_frame_configure(self,canvas):
        canvas.configure(scrollregion=canvas.bbox("all"))

    def enable_scrolling(self, canvas, event=None):
        #get the position of the most bottom most right frame
        #get the maximum values of all the frames
        max_x = max(self.selected_object_plate.frames['frame_plate_info'].winfo_x(),
                    self.selected_object_plate.frames['frame_job_info'].winfo_x(),
                    self.selected_object_plate.frames['frame_preview'].winfo_x() + self.selected_object_plate.frames['frame_preview'].winfo_width() + 20)

        max_y = max(self.selected_object_plate.frames['frame_plate_info'].winfo_y(),
                    self.selected_object_plate.frames['frame_job_info'].winfo_y(),
                    self.selected_object_plate.frames['frame_plot_settings'].winfo_y() + self.selected_object_plate.frames['frame_plot_settings'].winfo_height() + 20)
        
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
            object_plate = PlateAnalyzer(file_path)
            if object_plate.name in self.tabs.keys():
                del object_plate
                return
            
            self.selected_object_plate = object_plate
            self.tabs[object_plate.name] = object_plate
            title = '  ' + object_plate.name + '  '

            # create a frame for the new tab
            frame_main = tk.Frame(self.notebook)
            self.notebook.insert(len(self.notebook.tabs()) - 1, frame_main, text=title)
            object_plate.frames['frame_root'] = frame_main

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
            self.add_frame_plate_info(object_plate,container)
            self.add_frame_job_info(object_plate,container)
            self.add_frame_data_selection(object_plate,container)
            self.add_frame_figure_handle(object_plate,container)
            self.add_frame_figure_selection(object_plate,container)
            self.add_frame_plot_settings(object_plate,container)
            self.add_frame_preview(object_plate,container)
            self.add_frame_template(object_plate,container)
            
    def add_frame_plate_info(self, object_plate, parent_frame):
        #create a frame for the plate info
        frame_plate_info = LabelFrame(parent_frame, text="Plate Info", width=475, height=200)
        frame_plate_info.grid(row=0, column=0, columnspan=10, padx=10, pady=10, sticky='nws')
        frame_plate_info.grid_propagate(flag=False)
        object_plate.frames['frame_plate_info'] = frame_plate_info

        row_idx, col_idx = 0, 0
        #fill the frame with data - plate info
        for item in object_plate.df_plate:
            name, value = item
            Label(frame_plate_info, text=name).grid(row=row_idx, column=col_idx, sticky='w', padx=5, pady=2)
            Label(frame_plate_info, text=value).grid(row=row_idx, column=col_idx+1, sticky='w', padx=5, pady=2)
            row_idx = row_idx + 1
            if row_idx > 7:
                row_idx = 0
                col_idx = 2

        # force update to ensure the tab is fully rendered
        self.root.update_idletasks()
            
    def add_frame_job_info(self, object_plate, parent_frame):
        frame_job_info = LabelFrame(parent_frame, text="Job Info")
        frame_job_info.grid(row=0, column=11, columnspan=10, padx=10, pady=10, sticky='news')
        #frame_job_info.grid_propagate(flag=False)
        object_plate.frames['frame_job_info'] = frame_job_info

        #get height of the frame_plate_info and create a canvas
        height_frame_plate_info = object_plate.frames['frame_plate_info'].winfo_height()
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
        for col_idx, item in enumerate(object_plate.df_job[0]):
           Label(help_frame, text=item).grid(row=0, column=col_idx, sticky='', padx=10, pady=2)
        
        col_widths = []
        for col_idx in range(len(object_plate.df_job[0])):
            col_widths.append(len(object_plate.df_job[0][col_idx])-2)


        # fill the frame with data - job info
        for row_idx, row in enumerate(object_plate.df_job[1:]):
            for col_idx, item in enumerate(row):
                Label(container, text=item, width=col_widths[col_idx]).grid(row=row_idx, column=col_idx, sticky='', padx=10, pady=2)
                #Label(container, text=item).grid(row=row_idx, column=col_idx, sticky='', padx=5, pady=2)
                

        # force update to ensure the tab is fully rendered
        self.root.update_idletasks()

    def add_frame_data_selection(self, object_plate, parent_frame):
        #get height of the screen and adjust height to fill the screen minus height of plate_frame_info minus some padding
        available_height = self.root.winfo_screenheight() - object_plate.frames['frame_plate_info'].winfo_height() - object_plate.frames['frame_plate_info'].winfo_height() - 85
        
        frame_data_selection = LabelFrame(parent_frame, text="Data slection", width=146, height=(available_height+24))
        frame_data_selection.grid(row=2, column=0, rowspan=6, padx=10, pady=10, sticky='news')
        frame_data_selection.grid_propagate(flag=False)
        object_plate.frames['frame_data_selection'] = frame_data_selection
        object_plate.selected_data = [tk.IntVar() for i in range(len(object_plate.df_data.columns))]

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
        
        checkbox = [None] * len(object_plate.df_data.columns)
        #create a one column of checkboxes from df_data.columns
        for index, col in enumerate(object_plate.df_data.columns):
            checkbox[index] = Checkbutton(container, text=col, variable=object_plate.selected_data[index], onvalue=1, offvalue=0, command=lambda: self.frame_data_selection_checkbox_enable(object_plate, checkbox))
            checkbox[index].grid(row=index, column=0, sticky='w', padx=5, pady=2)
            

        
        self.bind_to_widget_and_children(canvas, "<Button-3>", lambda event: self.frame_data_selection_checkbox_enable(object_plate, checkbox))
        self.bind_to_widget_and_children(canvas, "<Button-3>", lambda event: self.uncheck_all(container, object_plate, checkbox))
        #lambda: self.frame_data_selection_checkbox_enable(object_plate, checkbox)
        self.root.update_idletasks()

    def frame_data_selection_checkbox_enable(self, object_plate, checkbox):
        sum = 0
        for var in object_plate.selected_data:
            sum += var.get()

        # if there are more than 8 selected, unselect all others
        if sum >= 8:
            for index, var in enumerate(object_plate.selected_data):
                if var.get() == 0:
                    checkbox[index].config(state=DISABLED)
        else:
            for index, var in enumerate(object_plate.selected_data):
                    checkbox[index].config(state=NORMAL)

    def bind_to_widget_and_children(self,widget, event, handler):
            widget.bind(event, handler)
            for child in widget.winfo_children():
                self.bind_to_widget_and_children(child, event, handler)

        
    def uncheck_all(self, container, object_plate, checkbox,event=None):
        for child in container.winfo_children():
            child.deselect()

        for var in object_plate.selected_data:
            var.set(0)

        for index, var in enumerate(object_plate.selected_data):
            checkbox[index].config(state=NORMAL)

    def add_frame_figure_handle(self, object_plate, parent_frame):
        frame_figure_handle = Frame(parent_frame)
        frame_figure_handle.grid(row=1,column=0, columnspan=3, sticky='news', pady=10, padx=10)
        object_plate.frames['frame_figure_handle'] = frame_figure_handle

        Button(frame_figure_handle, text='New figure\n--->', command=lambda :self.add_new_figure(object_plate)).grid(row=1, column=0, pady=10)
        Button(frame_figure_handle, text='Delete figure\n<---', command=None).grid(row=1, column=1, pady=10, sticky='w')
        #Button(frame_figure_handle, text='Plot', command=None).grid(row=2, column=1, pady=10, padx=10, sticky='news')

        Label(frame_figure_handle, text='Figure name:  ').grid(row=0, column=0, sticky='', pady=10)
        figure_entry_name = Entry(frame_figure_handle, width=50)
        figure_entry_name.grid(row=0, column=1, columnspan=10, sticky='', pady=10)
        object_plate.figure_entry_name = figure_entry_name

    def add_frame_figure_selection(self, object_plate, parent_frame):
        frame_figure_selection = LabelFrame(parent_frame, text='Figures', width=1170, height=102)
        frame_figure_selection.grid(row=1, column=11, columnspan=12, sticky='news', padx=10, pady=10)
        frame_figure_selection.grid_propagate(flag=False)
        object_plate.frames['frame_figure_selection'] = frame_figure_selection
        
        object_plate.notebook_figures_selection = ttk.Notebook(frame_figure_selection)
        object_plate.notebook_figures_selection.grid(row=0, column=0, sticky='news')
        frame_figure_selection.grid_rowconfigure(0, weight=1)
        frame_figure_selection.grid_columnconfigure(0, weight=1)

        object_plate.notebook_figures_selection.bind("<Button-1>", lambda event: self.on_tab_click('notebook_figures_selection', event))
        object_plate.notebook_figures_selection.bind("<Button-3>", lambda event: self.on_tab_right_click('notebook_figures_selection',event))
        
        self.root.update_idletasks()

    def get_memory_usage(self):
        
        process = psutil.Process(os.getpid())
        print(f"Memory usage: {process.memory_info().rss / 1024 / 1024} MB") # in bytes process.memory_info().rss / 1024 / 1024
    
    def add_frame_plot_settings(self, object_plate, parent_frame):
        frame_plot_settings = LabelFrame(parent_frame, text='Plot settings', height=350, width=450)
        frame_plot_settings.grid(row=2, column=21, columnspan=2, rowspan=6, sticky='news', padx=10, pady=10)
        frame_plot_settings.grid_propagate(flag=False)
        frame_plot_settings.grid_rowconfigure(0, weight=1)
        frame_plot_settings.grid_columnconfigure(0, weight=1)
        
        
        object_plate.frames['frame_plot_settings'] = frame_plot_settings
        
        self.root.update_idletasks()

    def add_frame_preview(self, object_plate, parent_frame):
        frame_preview = LabelFrame(parent_frame, text='Preview', width=200, height=100)
        frame_preview.grid(row=2, column=1, columnspan=20, rowspan=6, pady=10, padx=10, sticky='news')
        #frame_preview.grid_propagate(flag=False)
        object_plate.frames['frame_preview'] = frame_preview

        canvas = Canvas(frame_preview)
        canvas.grid(row=0, column=0, sticky='news')

        self.root.update_idletasks()

    def add_frame_template(self, object_plate, parent_frame):
        frame_template = LabelFrame(parent_frame, text='Template', height=150, width=200)
        frame_template.grid(row=0, column=21, sticky='news', pady=10, padx=10)
        object_plate.frames['frame_template'] = frame_template

        self.root.update_idletasks()

    def add_new_figure(self, object_plate):
        new_figure_name = object_plate.figure_entry_name.get()
        if new_figure_name not in object_plate.figures.keys() and new_figure_name != '':
            new_figure = AddFigure(new_figure_name)
            object_plate.figures[new_figure_name] = new_figure 
            frame = Frame(object_plate.notebook_figures_selection)
            object_plate.notebook_figures_selection.add(frame, text=new_figure_name)
            object_plate.notebook_figures_selection.select(frame)

            # create labels of data we want to plot
            row_idx, col_idx = 0, 0
            for index, var in enumerate(object_plate.selected_data):
                if var.get() == 1:
                    item = '  ' + object_plate.df_data.columns[index] + '  '
                    Label(frame, text=item).grid(row=row_idx, column=col_idx, sticky='w', padx=10, pady=5)
                    row_idx += 1
                    if row_idx >= 2:
                        row_idx = 0
                        col_idx += 1

            # adding data to the object
            for index, checked_box in enumerate(object_plate.selected_data):
                if int(checked_box.get()) == 1:
                    axis_name = object_plate.df_data.columns[index]
                    new_figure.add_ax(object_plate.df_data.columns[index], object_plate.df_data[axis_name])
            new_figure.x_range[0] = object_plate.df_data.index.min()
            new_figure.x_range[1] = object_plate.df_data.index.max()

            self.create_separated_frame(object_plate, new_figure)

        self.root.update_idletasks()

    def create_separated_frame(self, object_plate, new_figure):
        frame_plot_settings_inner = Frame(object_plate.frames['frame_plot_settings'])
        frame_plot_settings_inner.grid(row=0, column=0, sticky='news')
        frame_plot_settings_inner.grid_propagate(flag=False)
        frame_plot_settings_inner.grid_columnconfigure(0, weight=1)
        
        object_plate.frames['frame_plot_settings_inner'][new_figure.name] = frame_plot_settings_inner

        dict_of_global_widgets = {}

        figure_name_label = Label(frame_plot_settings_inner, text='Figure name')
        figure_name_label.grid(row=0, column=0, sticky='w', padx=10, pady=10)

        figure_name_entry = Entry(frame_plot_settings_inner, width=55)
        figure_name_entry.grid(row=0, column=1, columnspan=5, sticky='e', padx=10, pady=10)
        figure_name_entry.insert(0,new_figure.name)
        dict_of_global_widgets['figure_name'] = figure_name_entry

        notebook = ttk.Notebook(frame_plot_settings_inner)
        notebook.grid(row=1, column=0, columnspan=5, sticky='news')
        
        button_plot = Button(frame_plot_settings_inner, text='PLOT', command=lambda :self.plot_update(preview=False))
        button_plot.grid(row=3, column=0, columnspan=5, sticky='news')

        button_preview = Button(frame_plot_settings_inner, text='Preview', command=lambda :self.plot_update(preview=True))
        button_preview.grid(row=4, column=0, columnspan=5, sticky='news')

        
        x_range_label = Label(frame_plot_settings_inner, text='X range')
        x_range_label.grid(row=2, column=0, sticky='w', padx=10, pady=10)
        
        x_range_label_min = Label(frame_plot_settings_inner, text='min', width=3)
        x_range_label_min.grid(row=2, column=1, sticky='w', padx=1, pady=10)
        
        x_range_entry_min = Entry(frame_plot_settings_inner, width=10)
        x_range_entry_min.insert(0,'auto')
        x_range_entry_min.grid(row=2, column=2, sticky='w', padx=1, pady=10)
        dict_of_global_widgets['x_range_min'] = x_range_entry_min
        
        
        x_range_label_max = Label(frame_plot_settings_inner, text='max', width=3)
        x_range_label_max.grid(row=2, column=3, sticky='w', padx=1, pady=10)

        x_range_entry_max = Entry(frame_plot_settings_inner, width=10)
        x_range_entry_max.insert(0,'auto')
        x_range_entry_max.grid(row=2, column=4, sticky='w', padx=1, pady=10)
        dict_of_global_widgets['x_range_max'] = x_range_entry_max

        new_figure.figure_settings =  dict_of_global_widgets

        for ax_number, ax in enumerate(new_figure.axes):
            tab = Frame(notebook)

            name = ax['name']
            index = name.find('[')-1  # Find the index of the first '['
            name = name[:index] # Name without brackets
            
            
            notebook.add(tab, text=name)
            
            # dict of assigned variables
            dict_of_local_widgets = {}

            axis_name_label = Label(tab, text=ax['name'])
            axis_name_label.grid(row=0, column=0, columnspan=5, padx=10, pady=10, sticky='w')

            axis_label_label = Label(tab, text='Axis label')
            axis_label_label.grid(row=1, column=0, padx=10, pady=10, sticky='w')

            axis_label_entry = Entry(tab)
            axis_label_entry.grid(row=1, column=1, columnspan=4, padx=1, pady=10, sticky='w')
            axis_label_entry.insert(0,ax['name']) #default name of the axis label
            dict_of_local_widgets['axis_label'] = axis_label_entry

            legend_label_label = Label(tab, text='Legend label')
            legend_label_label.grid(row=2, column=0, padx=10, pady=10, sticky='w')

            
            legend_label_entry = Entry(tab)
            legend_label_entry.grid(row=2, column=1, columnspan=4, sticky='w', padx=1, pady=10)
            legend_label_entry.insert(0,ax['name']) #default name of the legend label
            dict_of_local_widgets['legend_label'] = legend_label_entry

            y_range_label = Label(tab, text='Y range')
            y_range_label.grid(row=4, column=0, sticky='w', padx=10, pady=10)

            y_range_label_min = Label(tab, text='min', width=3)
            y_range_label_min.grid(row=4, column=1, sticky='w', padx=1, pady=10)

            y_range_entry_min = Entry(tab, width=10)
            y_range_entry_min.insert(0,'auto')
            y_range_entry_min.grid(row=4, column=2, sticky='w', padx=1, pady=10)
            dict_of_local_widgets['y_range_min'] = y_range_entry_min

            y_range_label_max = Label(tab, text='max', width=3)
            y_range_label_max.grid(row=4, column=3, sticky='w', padx=1, pady=10)

            y_range_entry_max = Entry(tab, width=10)
            y_range_entry_max.insert(0,'auto')
            y_range_entry_max.grid(row=4, column=4, sticky='w', padx=1, pady=10)
            dict_of_local_widgets['y_range_max'] = y_range_entry_max

            y_ax_number_label = Label(tab, text='Y axis position')
            y_ax_number_label.grid(row=5, column=0, sticky='w', padx=10, pady=10)

            y_ax_number_combobox = ttk.Combobox(tab, values=[i for i in range(0,8)], state="readonly", width=10)
            y_ax_number_combobox.grid(row=5, column=1, columnspan=4, sticky='w', padx=1, pady=10)
            y_ax_number_combobox.set(0)
            dict_of_local_widgets['y_ax_number'] = y_ax_number_combobox

            color_label = Label(tab, text='Color')
            color_label.grid(row=6, column=0, sticky='w', padx=10, pady=10)

            color_combobox = ttk.Combobox(tab, values=new_figure.color_list, state="readonly", width=10)
            color_combobox.grid(row=6, column=1, columnspan=4, sticky='w', padx=1, pady=10)
            color_combobox.set(new_figure.color_list[ax_number])
            dict_of_local_widgets['color'] = color_combobox

            line_width_label = Label(tab, text='Line width')
            line_width_label.grid(row=7, column=0, sticky='w', padx=10, pady=10)


            line_width_entry = Entry(tab, width=10)
            line_width_entry.grid(row=7, column=1, columnspan=4, sticky='w', padx=1, pady=10)
            line_width_entry.insert(0,1)
            dict_of_local_widgets['line_width'] = line_width_entry

            grid_on_label = Label(tab, text='Grid on')
            grid_on_label.grid(row=8, column=0, sticky='w', padx=10, pady=10)

            var = BooleanVar()
            grid_on_checkbutton = Checkbutton(tab, variable=var, width=5)
            grid_on_checkbutton.grid(row=8, column=1, sticky='w', columnspan=4, padx=10, pady=10)
            dict_of_local_widgets['grid_on'] = var

            hide_axis_label = Label(tab, text='Hide axis')
            hide_axis_label.grid(row=9, column=0, sticky='w', padx=10, pady=10)

            var = BooleanVar()
            hide_axis_checkbutton = Checkbutton(tab, variable=var, width=5)
            hide_axis_checkbutton.grid(row=9, column=1, sticky='w', columnspan=4, padx=10, pady=10)
            dict_of_local_widgets['hide_axis'] = var
            
            #tab.grid_propagate(flag=False)
            new_figure.plot_settings[ax['name']] =  dict_of_local_widgets

        #self.plot_update()
        #new_figure.show_figure(plot=False) # plot a preview

        #print(object_plate.frames['frame_plot_settings_inner'].items())
        """for key, value in new_figure.plot_settings.items():
            print(key)
            for key1, value1 in value.items():
                print('   ' + key1, value1)
            print('\n\n')"""
        
    def plot_update(self, preview):

        selected_index = self.selected_object_plate.notebook_figures_selection.index(self.selected_object_plate.notebook_figures_selection.select())
        print("Selected tab index:", selected_index)

        # Optionally, get the text (name) of the selected tab
        tab_text = self.selected_object_plate.notebook_figures_selection.tab(selected_index, "text").replace(" ","")
        print("Selected tab text:", tab_text)

        self.selected_object_plate.figures[tab_text].name = self.selected_object_plate.figures[tab_text].figure_settings['figure_name'].get()
        x_range_min = self.selected_object_plate.figures[tab_text].figure_settings['x_range_min'].get()
        x_range_max = self.selected_object_plate.figures[tab_text].figure_settings['x_range_max'].get()

        self.selected_object_plate.figures[tab_text].x_range[0], self.selected_object_plate.figures[tab_text].x_range[1] = self.get_x_axis_range(tab_text, x_range_min, x_range_max)

        for ax in self.selected_object_plate.figures[tab_text].axes:
            axis_label = self.selected_object_plate.figures[tab_text].plot_settings[ax['name']]['axis_label'].get()
            axis_label = self.selected_object_plate.figures[tab_text].plot_settings[ax['name']]['axis_label'].get()
            y_range_min = self.selected_object_plate.figures[tab_text].plot_settings[ax['name']]['y_range_min'].get()
            y_range_max = self.selected_object_plate.figures[tab_text].plot_settings[ax['name']]['y_range_max'].get()
            legend_label = self.selected_object_plate.figures[tab_text].plot_settings[ax['name']]['legend_label'].get()
            y_ax_number = self.selected_object_plate.figures[tab_text].plot_settings[ax['name']]['y_ax_number'].get()
            color = self.selected_object_plate.figures[tab_text].plot_settings[ax['name']]['color'].get()
            line_width = self.selected_object_plate.figures[tab_text].plot_settings[ax['name']]['line_width'].get()
            hide_axis = self.selected_object_plate.figures[tab_text].plot_settings[ax['name']]['hide_axis'].get()

            y_range_min, y_range_max = self.get_y_axis_range(ax, y_range_min, y_range_max)

            print('\n***' + ax['name'] + '***')
            print(axis_label)
            print(y_range_min)
            print(y_range_max)
            print(legend_label)
            print(y_ax_number)
            print(color)
            print(line_width)
            print(hide_axis)
            print('---------------------\n\n')

            self.selected_object_plate.figures[tab_text].update_axis(ax['name'], axis_label, legend_label, y_range_min, y_range_max, y_ax_number, color, line_width, hide_axis)
        
        frame_preview_height = self.selected_object_plate.frames['frame_preview'].winfo_height()
        frame_preview_width = self.selected_object_plate.frames['frame_preview'].winfo_width()

        fig = self.selected_object_plate.figures[tab_text].show_figure(preview, frame_preview_width-20, frame_preview_height-20)

        if preview is True:
            for widget in self.selected_object_plate.frames['frame_preview'].winfo_children():
                widget.destroy()

            canvas = FigureCanvasTkAgg(fig, master=self.selected_object_plate.frames['frame_preview'])
            canvas.draw()
        
            canvas.get_tk_widget().pack()

    

    def get_x_axis_range(self, tab_text, x_range_min, x_range_max):
        x_range_min_def = self.selected_object_plate.df_data.index.min()
        x_range_max_def = self.selected_object_plate.df_data.index.max()
        x_range_def = x_range_max_def - x_range_min_def
        x_range_diff = x_range_def * 0.05

        x_range = [0, 0]
        if x_range_min == 'auto':
            x_range[0] = x_range_min_def - x_range_diff
            print('min autoautoautoautoautoautoauto')
        else:
            x_range[0] = float(x_range_min)

        if x_range_max == 'auto':
            print('max autoautoautoautoautoautoauto')
            x_range[1] = x_range_max_def + x_range_diff
        else:
            x_range[1] = float(x_range_max)
        
        print(f"min {x_range[0]}", f"max {x_range[1]}")
        return x_range[0], x_range[1]
    

    def get_y_axis_range(self, axis, y_range_min, y_range_max):
        y_range_min_def = axis['data'].min()
        y_range_max_def = axis['data'].max()
        y_range_def = y_range_max_def- y_range_min_def
        y_range_diff = y_range_def * 0.05

        y_range = [0, 0]

        if y_range_min == 'auto':
            y_range[0] = y_range_min_def - y_range_diff
        else:
            y_range[0] = float(y_range_min)

        if y_range_max == 'auto':
            y_range[1] = y_range_max_def + y_range_diff
        else:
            y_range[1] = float(y_range_max)
        
        return y_range[0], y_range[1]

   
    def add_plus_tab(self):
        frame = tk.Frame(self.notebook)
        self.notebook.add(frame, text=self.plus_tab_label)

    def on_tab_right_click(self, source, event=None):
        if source == 'notebook_main':
            try:
                print('right click')
                tab_id = self.notebook.index(f"@{event.x},{event.y}")
                print('right_click ',type(tab_id), tab_id)
            except tk.TclError:
                return
                
            #check if the tab is equal to + sign
            tab_text = self.notebook.tab(tab_id, option="text")

            if tab_text != self.plus_tab_label:
                self.close_tab(tab_id,source)

            print('notebook_main')
        elif source == 'notebook_figures_selection':
            try:
                print('right click')
                tab_id = self.selected_object_plate.notebook_figures_selection.index(f"@{event.x},{event.y}")
                print('right_click ',type(tab_id), tab_id)
            except tk.TclError:
                return
            
            print('notebook_figure_selection')
            self.close_tab(tab_id,source)
        else:
            print('wefwsfwsfrfrsfgrgrsegeg')

        # force update to ensure the tab is fully rendered
        self.root.update_idletasks()

    def on_tab_click(self, source, event=None):
        if source == 'notebook_main':
            try:
                tab_id = self.notebook.index(f"@{event.x},{event.y}")
            except tk.TclError:
                return

            #check if the tab is equal to + sign
            tab_text = self.notebook.tab(tab_id, option="text")

            if tab_text == self.plus_tab_label:
                self.add_tab()
                self.notebook.select(len(self.notebook.tabs()) - 2)
            else:
                self.selected_object_plate = self.tabs[tab_text.replace(" ", "")]
        elif source == 'notebook_figures_selection':
            try:
                tab_id = self.selected_object_plate.notebook_figures_selection.index(f"@{event.x},{event.y}")
            except tk.TclError:
                return
            
            print(tab_id)
            tab_text = self.selected_object_plate.notebook_figures_selection.tab(tab_id, option="text")
            print(tab_text)
            self.selected_object_plate.frames['frame_plot_settings_inner'][tab_text].tkraise()

        # force update to ensure the tab is fully rendered
        self.root.update_idletasks()
            
    

    def close_tab(self, tab_id, source=None):
        if source == 'notebook_main' or source == None:
            tab_index = self.notebook.index(tab_id)

            tab_text = self.notebook.tab(tab_id, option="text").replace(" ", "")
            print(tab_text)
            print(self.tabs[tab_text])

            index = self.tabs[tab_text]
            print('tab index after close is' + str(index))
            del self.tabs[tab_text]

            # Get the widget name associated with the tab index
            tab_widget_name = self.notebook.tabs()[tab_index]
            frame = self.notebook.nametowidget(tab_widget_name)

            frame.destroy()

            if int(tab_index) > 0:
                self.notebook.select(tab_index-1)
                
            # Get the index of the currently selected tab
            selected_index = self.notebook.index(self.notebook.select())
    
            # Get the text of the selected tab
            tab_text = self.notebook.tab(selected_index, "text").replace(" ","")
            if tab_text != self.plus_tab_label.replace(" ",""):
                self.selected_object_plate = self.tabs[tab_text]

        elif source == 'notebook_figures_selection':
            tab_index = self.selected_object_plate.notebook_figures_selection.index(tab_id)

            tab_text = self.selected_object_plate.notebook_figures_selection.tab(tab_id, option="text").replace(" ", "")

            selected_tab_id = self.notebook.select()
    
            # Get the text (name) of the selected tab
            tab_text_main = self.notebook.tab(selected_tab_id, "text")

            tab_text_main = tab_text_main.replace(" ", "")

            

            print(tab_text)
            
            # Get the widget name associated with the tab index
            tab_widget_name = self.selected_object_plate.notebook_figures_selection.tabs()[tab_index]
            frame = self.selected_object_plate.notebook_figures_selection.nametowidget(tab_widget_name)

            for frame_inner in self.selected_object_plate.frames['frame_plot_settings_inner'].values():
                frame_inner.destroy()

            frame.destroy()

            object_plate_name = self.selected_object_plate.name
            del self.tabs[object_plate_name].figures[tab_text]
            

        # force update to ensure the tab is fully rendered
        self.root.update_idletasks()
       
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
        file_menu.add_command(label="Close this tab", accelerator="            Ctrl + Q", command=lambda :self.on_tab_right_click(source='notebook_main'))
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
        print('close this tab')
        tab_id = self.notebook.select()
        tab_text = self.notebook.tab(tab_id, option="text")
        print(tab_id, tab_text, self.plus_tab_label)
        if tab_text != self.plus_tab_label:
            self.close_tab(tab_id)

        

    def save(self, event=None):

        print('Save')
    
    def save_as(self, event=None):
        gc.collect()
        print('Save as')
    
    def get_help(self,event=None):
        self.get_memory_usage()
        #print(self.tabs.items())
        #width = self.selected_object_plate.frames['frame_figure_selection'].winfo_width()
        #height = self.selected_object_plate.frames['frame_figure_selection'].winfo_height()
        #print(width, height)


    def exit_app(self,event=None):
        self.root.destroy()
