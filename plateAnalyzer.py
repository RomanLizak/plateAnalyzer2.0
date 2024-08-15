import io
import os
import pandas as pd

class PlateAnalyzer:
    # starting position of data tables inside the csv file
    #[row, col]
    plate_table_start, plate_table_end = [1, 3], [17, 5]
    job_table_start, job_table_end = [20, 2], [None, 9] # we dont know where it ends, we will find out from the plate_table later
    data_table_start, data_table_end = [45, 2], [None, None] # we dont know how many rows it has, we will go the end. we know how many columns but it can change in the future so it will be dynamic
    ROW = 0
    COL = 1

    def __init__(self, file_path):
        self.name, self.df_plate, self.df_job, self.df_data = self.initialize_csv(file_path)
        self.frames = {
            'frame_root': None,
            'frame_main': None,
            'frame_plate_info': None,
            'frame_job_info': None,
            'frame_data_selection': None,
            'frame_figure_handle': None,
            'frame_figure_selection': None,
            'frame_plot_settings': None,
            # holds each frame in frame_plot_settings
            'frame_plot_settings_inner': {},
            'frame_preview': None,
            'frame_template':None
        }
        
        self.selected_data = None
        self.figures = {}
        self.figure_entry_name = None
        self.notebook_figure_selection = None

    
    @classmethod
    def initialize_csv(cls, file_path):
        # Read the CSV file into a pandas DataFrame
        with open(file_path, 'r') as file_csv:
            lines = file_csv.readlines()
        
        # Determine the maximum number of columns
        max_cols = max(len(line.strip().split(';')) for line in lines)

        # Preprocess each line to ensure it has the same number of columns
        preprocessed_data = []
        for line in lines:
            cols = line.strip().split(';')
            padded_cols = cols + [''] * (max_cols - len(cols))  # Pad with empty strings
            preprocessed_data.append(';'.join(padded_cols))

        # Join the preprocessed lines into a single string
        preprocessed_csv = '\n'.join(preprocessed_data)
        
        # Use StringIO to convert the string to a file-like object
        csv_file_like = io.StringIO(preprocessed_csv)
        
        # Read the CSV data from the file-like object
        # proccess data dataframe
        # return pointer at the beginning of the file
        csv_file_like.seek(0)
        
        df_data = pd.read_csv(csv_file_like, header=None, decimal=',', sep=';', engine='python', encoding='ISO-8859-1')

        #read the plate table
        df_plate = df_data.iloc[cls.plate_table_start[cls.ROW]:cls.plate_table_end[cls.ROW],cls.plate_table_start[cls.COL]:(cls.plate_table_end[cls.COL])].values.tolist()
        df_plate = [row for row in df_plate if not pd.isnull(row[1])]
        
        
        #read from df_plate number of cycles
        for row in df_plate:
            name, value = row
            if "Total Cycles" in name:
                cls.job_table_end[cls.ROW] = cls.job_table_start[cls.ROW] + int(value) + 1
                break

        #read the job table
        df_job = df_data.iloc[cls.job_table_start[cls.ROW]:cls.job_table_end[cls.ROW],cls.job_table_start[cls.COL]:cls.job_table_end[cls.COL]].values.tolist()

        #read the header of data table
        df_data_header = df_data.iloc[(cls.data_table_start[cls.ROW]-1),cls.data_table_start[cls.COL]:]
        #read the data table
        df_data = df_data.iloc[cls.data_table_start[cls.ROW]:,cls.data_table_start[cls.COL]:]
        #add the header to the data table
        df_data.columns = df_data_header
        
        # Remove columns with 'Unnamed' in their names
        df_data = df_data.dropna(axis=1, how='any').reset_index(drop=True).astype(float)
        # Convert all columns to numeric, forcing errors to NaN (not a number)
        
        #return name of the file, df_plate, df_job, df_data
        return f"{os.path.splitext(os.path.basename(file_path))[0]}",df_plate, df_job, df_data



    
        

