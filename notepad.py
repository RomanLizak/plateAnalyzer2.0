import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import os
import psutil

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

        self.notebook_figures_selection = None

        self.add_plus_tab()
        
        self.notebook.bind("<Button-1>", lambda event: self.on_tab_click('notebook_main', event))
        self.notebook.bind("<Button-3>", lambda event: self.on_tab_right_click('notebook_main', event))

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
                    self.selected_object.frames['frame_plot_settings'].winfo_y() + self.selected_object.frames['frame_plot_settings'].winfo_height() + 20)
        
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
            self.add_frame_figure_handle(object,container)
            self.add_frame_figure_selection(object,container)
            self.add_frame_plot_settings(object,container)
            self.add_frame_preview(object,container)
            self.add_frame_template(object,container)
            
    def add_frame_plate_info(self, object, parent_frame):
        #create a frame for the plate info
        frame_plate_info = LabelFrame(parent_frame, text="Plate Info", width=475, height=200)
        frame_plate_info.grid(row=0, column=0, columnspan=10, padx=10, pady=10, sticky='nws')
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
        frame_job_info.grid(row=0, column=11, columnspan=10, padx=10, pady=10, sticky='news')
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
        #get height of the screen and adjust height to fill the screen minus height of plate_frame_info minus some padding
        available_height = self.root.winfo_screenheight() - object.frames['frame_plate_info'].winfo_height() - object.frames['frame_plate_info'].winfo_height() - 85
        
        frame_data_selection = LabelFrame(parent_frame, text="Data slection", width=146, height=(available_height+24))
        frame_data_selection.grid(row=2, column=0, rowspan=6, padx=10, pady=10, sticky='news')
        frame_data_selection.grid_propagate(flag=False)
        object.frames['frame_data_selection'] = frame_data_selection
        object.selected_data = [tk.IntVar() for i in range(len(object.df_data.columns))]

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
        
        checkbox = [None] * len(object.df_data.columns)
        #create a one column of checkboxes from df_data.columns
        for index, col in enumerate(object.df_data.columns):
            checkbox[index] = Checkbutton(container, text=col, variable=object.selected_data[index], onvalue=1, offvalue=0, command=lambda: self.frame_data_selection_checkbox_enable(object, checkbox))
            checkbox[index].grid(row=index, column=0, sticky='w', padx=5, pady=2)
            

        
        self.bind_to_widget_and_children(canvas, "<Button-3>", lambda event: self.frame_data_selection_checkbox_enable(object, checkbox))
        self.bind_to_widget_and_children(canvas, "<Button-3>", lambda event: self.uncheck_all(container, object, checkbox))
        #lambda: self.frame_data_selection_checkbox_enable(object, checkbox)
        self.root.update_idletasks()

    def frame_data_selection_checkbox_enable(self, object, checkbox):
        sum = 0
        for var in object.selected_data:
            sum += var.get()

        # if there are more than 8 selected, unselect all others
        if sum >= 8:
            for index, var in enumerate(object.selected_data):
                if var.get() == 0:
                    checkbox[index].config(state=DISABLED)
        else:
            for index, var in enumerate(object.selected_data):
                    checkbox[index].config(state=NORMAL)

    def bind_to_widget_and_children(self,widget, event, handler):
            widget.bind(event, handler)
            for child in widget.winfo_children():
                self.bind_to_widget_and_children(child, event, handler)

        
    def uncheck_all(self, container, object, checkbox,event=None):
        for child in container.winfo_children():
            child.deselect()

        for var in object.selected_data:
            var.set(0)

        for index, var in enumerate(object.selected_data):
            checkbox[index].config(state=NORMAL)

    def add_frame_figure_handle(self, object, parent_frame):
        frame_figure_handle = Frame(parent_frame)
        frame_figure_handle.grid(row=1,column=0, columnspan=3, sticky='news', pady=10, padx=10)
        object.frames['frame_figure_handle'] = frame_figure_handle

        Button(frame_figure_handle, text='New figure\n--->', command=lambda :self.add_new_figure(object)).grid(row=1, column=0, pady=10)
        Button(frame_figure_handle, text='Delete figure\n<---', command=None).grid(row=1, column=1, pady=10, sticky='w')
        #Button(frame_figure_handle, text='Plot', command=None).grid(row=2, column=1, pady=10, padx=10, sticky='news')

        Label(frame_figure_handle, text='Figure name:  ').grid(row=0, column=0, sticky='', pady=10)
        figure_entry_name = Entry(frame_figure_handle, width=50)
        figure_entry_name.grid(row=0, column=1, columnspan=10, sticky='', pady=10)
        self.figure_entry_name = figure_entry_name

    def add_frame_figure_selection(self, object, parent_frame):
        frame_figure_selection = LabelFrame(parent_frame, text='Figures', width=1170, height=102)
        frame_figure_selection.grid(row=1, column=11, columnspan=12, sticky='news', padx=10, pady=10)
        frame_figure_selection.grid_propagate(flag=False)
        object.frames['frame_figure_selection'] = frame_figure_selection
        
        self.notebook_figures_selection = ttk.Notebook(frame_figure_selection)
        self.notebook_figures_selection.grid(row=0, column=0, sticky='news')
        frame_figure_selection.grid_rowconfigure(0, weight=1)
        frame_figure_selection.grid_columnconfigure(0, weight=1)

        self.notebook_figures_selection.bind("<Button-1>", lambda event: self.on_tab_click('notebook_figures_selection', event))
        self.notebook_figures_selection.bind("<Button-3>", lambda event: self.on_tab_right_click('notebook_figures_selection',event))
        
        self.root.update_idletasks()

    def get_memory_usage(self):
        
        process = psutil.Process(os.getpid())
        print(f"Memory usage: {process.memory_info().rss / 1024 / 1024} MB") # in bytes process.memory_info().rss / 1024 / 1024
    
    def add_frame_plot_settings(self, object, parent_frame):
        frame_plot_settings = LabelFrame(parent_frame, text='Plot settings', height=350, width=450)
        frame_plot_settings.grid(row=2, column=21, columnspan=2, rowspan=6, sticky='news', padx=10, pady=10)
        frame_plot_settings.grid_propagate(flag=False)
        frame_plot_settings.grid_rowconfigure(0, weight=1)
        frame_plot_settings.grid_columnconfigure(0, weight=1)
        
        
        object.frames['frame_plot_settings'] = frame_plot_settings
        
        self.root.update_idletasks()

    def add_frame_preview(self, object, parent_frame):
        frame_preview = LabelFrame(parent_frame, text='Preview', width=200, height=100)
        frame_preview.grid(row=2, column=1, columnspan=20, rowspan=6, pady=10, padx=10, sticky='news')
        #frame_preview.grid_propagate(flag=False)
        object.frames['frame_preview'] = frame_preview

        canvas = Canvas(frame_preview)
        canvas.grid(row=0, column=0, sticky='news')

        self.root.update_idletasks()

    def add_frame_template(self, object, parent_frame):
        frame_template = LabelFrame(parent_frame, text='Template', height=150, width=200)
        frame_template.grid(row=0, column=21, sticky='news', pady=10, padx=10)
        object.frames['frame_template'] = frame_template

        self.root.update_idletasks()

    def add_new_figure(self, object):
        new_figure_name = self.figure_entry_name.get()
        if new_figure_name not in AddFigure.get_all_figure_name() and new_figure_name != '':
            new_figure = AddFigure(new_figure_name)
            frame = Frame(self.notebook_figures_selection)
            self.notebook_figures_selection.add(frame, text=new_figure_name)
            self.notebook_figures_selection.select(frame)

            # create labels of data we want to plot
            row_idx, col_idx = 0, 0
            for index, var in enumerate(object.selected_data):
                if var.get() == 1:
                    item = '  ' + self.selected_object.df_data.columns[index] + '  '
                    Label(frame, text=item).grid(row=row_idx, column=col_idx, sticky='w', padx=10, pady=5)
                    row_idx += 1
                    if row_idx >= 2:
                        row_idx = 0
                        col_idx += 1

            # adding data to the object
            for index, checked_box in enumerate(object.selected_data):
                if int(checked_box.get()) == 1:
                    axis_name = object.df_data.columns[index]
                    new_figure.add_ax(object.df_data.columns[index], self.selected_object.df_data[axis_name])
        
            self.create_separated_frame(object, new_figure)

        self.root.update_idletasks()

    def create_separated_frame(self, object, new_figure):
        frame_plot_settings_inner = Frame(object.frames['frame_plot_settings'])
        frame_plot_settings_inner.grid(row=0, column=0, sticky='news')
        frame_plot_settings_inner.grid_propagate(flag=False)
        frame_plot_settings_inner.grid_columnconfigure(0, weight=1)
        object.frames['frame_plot_settings_inner'][new_figure.name] = frame_plot_settings_inner
        
        figure_name_label = Label(frame_plot_settings_inner, text='Figure name')
        figure_name_label.grid(row=0, column=0, sticky='w', padx=10, pady=10)

        figure_name_entry = Entry(frame_plot_settings_inner, width=55)
        figure_name_entry.grid(row=0, column=1, sticky='e', padx=10, pady=10)
        figure_name_entry.insert(0,new_figure.name)

        notebook = ttk.Notebook(frame_plot_settings_inner)
        notebook.grid(row=1, column=0, columnspan=2, sticky='news')
        
        for ax_number, ax in enumerate(new_figure.axes):
            tab = Frame(notebook)
            name = ax['name']
            index = name.find('[')-1  # Find the index of the first '['
            name = name[:index] # Name without brackets
            
            
            notebook.add(tab, text=name)
            print(type(ax['name']))
            
            # dict of assigned variables
            dict_of_widgets = {}

            axis_name_label = Label(tab, text=ax['name'])
            axis_name_label.grid(row=0, column=0, columnspan=2, sticky='ew', padx=10, pady=10)

            axis_label_label = Label(tab, text='Axis label')
            axis_label_label.grid(row=1, column=0, padx=10, pady=10)

            axis_label_entry = Entry(tab)
            axis_label_entry.grid(row=1, column=1, padx=10, pady=10)
            axis_label_entry.insert(0,ax['name']) #default name of the axis label
            dict_of_widgets['axis_label'] = axis_label_entry

            legend_label_label = Label(tab, text='Legend label')
            legend_label_label.grid(row=2, column=0, padx=10, pady=10)

            
            legend_label_entry = Entry(tab)
            legend_label_entry.grid(row=2, column=1, padx=10, pady=10)
            legend_label_entry.insert(0,ax['name']) #default name of the legend label
            dict_of_widgets['legend_label'] = legend_label_entry


            x_range_label = Label(tab, text='X range')
            x_range_label.grid(row=3, column=0, padx=10, pady=10)

            
            x_range_entry = Entry(tab)
            x_range_entry.grid(row=3, column=1, padx=10, pady=10)
            dict_of_widgets['x_range'] = x_range_entry

            y_limit_label = Label(tab, text='Y range')
            y_limit_label.grid(row=4, column=0, padx=10, pady=10)

            
            y_range_entry = Entry(tab)
            y_range_entry.grid(row=4, column=1, padx=10, pady=10)
            dict_of_widgets['y_range'] = y_range_entry

            y_ax_number_label = Label(tab, text='Y axis position')
            y_ax_number_label.grid(row=5, column=0, padx=10, pady=10)

            y_ax_number_combobox = ttk.Combobox(tab, values=[i for i in range(0,8)])
            y_ax_number_combobox.grid(row=5, column=1, padx=10, pady=10)
            y_ax_number_combobox.set(ax_number)
            dict_of_widgets['y_ax_number'] = y_ax_number_combobox

            color_label = Label(tab, text='Color')
            color_label.grid(row=6, column=0, padx=10, pady=10)

            color_combobox = ttk.Combobox(tab, values=new_figure.color_list)
            color_combobox.grid(row=6, column=1, padx=10, pady=10)
            color_combobox.set(new_figure.color_list[ax_number])
            dict_of_widgets['color'] = color_combobox

            line_width_label = Label(tab, text='Line width')
            line_width_label.grid(row=7, column=0, padx=10, pady=10)


            line_width_entry = Entry(tab)
            line_width_entry.grid(row=7, column=1, padx=10, pady=10)
            line_width_entry.insert(0,1)
            dict_of_widgets['line_width'] = line_width_entry
            

            new_figure.plot_settings[ax['name']] =  dict_of_widgets

        #print(object.frames['frame_plot_settings_inner'].items())
        for key, value in new_figure.plot_settings.items():
            print(key)
            for key1, value1 in value.items():
                print('   ' + key1, value1)
            print('\n\n')

    #add the first tab to the notebook
    def add_plus_tab(self):
        frame = tk.Frame(self.notebook)
        self.notebook.add(frame, text=self.plus_tab_label)

    def on_tab_right_clicks(self, source, event=None):
        if source == 'notebook_main':
            try:
                tab_id = self.notebook.index(f"@{event.x},{event.y}")
                print('right_click ', type(tab_id), tab_id)
            except tk.TclError:
                return

            # Check if the tab is equal to the + sign
            tab_text = self.notebook.tab(tab_id, option="text")

            if tab_text != self.plus_tab_label:
                self.close_tab(tab_id)
        elif source == 'notebook_figures_selection':
            print(source + 'ok')
        else:
            print('wefwsfwsfrfrsfgrgrsegeg')

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
                tab_id = self.notebook_figures_selection.index(f"@{event.x},{event.y}")
                print('right_click ',type(tab_id), tab_id)
            except tk.TclError:
                return
            
            print('notebook_figure_selection')
            self.close_tab(tab_id,source)
        else:
            print('wefwsfwsfrfrsfgrgrsegeg')

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
                self.selected_object = self.tabs[tab_text.replace(" ", "")]
        elif source == 'notebook_figures_selection':
            try:
                tab_id = self.notebook_figures_selection.index(f"@{event.x},{event.y}")
            except tk.TclError:
                return
            print(tab_id)
            tab_text = self.notebook_figures_selection.tab(tab_id, option="text")
            print(tab_text)
            self.selected_object.frames['frame_plot_settings_inner'][tab_text].tkraise()
        else:
            return
    

    def close_tab(self, tab_id, source=None):
        if source == 'notebook_main':
            tab_index = self.notebook.index(tab_id)

            tab_text = self.notebook.tab(tab_id, option="text").replace(" ", "")
            print(tab_text)
            print(self.tabs[tab_text])
            del self.tabs[tab_text]

            # Get the widget name associated with the tab index
            tab_widget_name = self.notebook.tabs()[tab_index]
            frame = self.notebook.nametowidget(tab_widget_name)

            frame.destroy()

            if int(tab_index) > 0:
                self.notebook.select(tab_index-1)

        elif source == 'notebook_figures_selection':
            tab_index = self.notebook_figures_selection.index(tab_id)

            tab_text = self.notebook_figures_selection.tab(tab_id, option="text").replace(" ", "")
            print(tab_text)
            
            # Get the widget name associated with the tab index
            tab_widget_name = self.notebook_figures_selection.tabs()[tab_index]
            frame = self.notebook_figures_selection.nametowidget(tab_widget_name)

            frame.destroy()

        #never select '+' tab
        
        
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
        print(self.tabs.items())
        width = self.selected_object.frames['frame_figure_selection'].winfo_width()
        height = self.selected_object.frames['frame_figure_selection'].winfo_height()
        print(width, height)


    def exit_app(self,event=None):
        self.root.destroy()
