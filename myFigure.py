import matplotlib.pyplot as plt
import ast
import numpy as np

class AddFigure():
    main_axis = 1
    figure_names = []
    color_list = ["red", "blue", "green", "orange", "purple", "brown", "pink", "gray"]

    def __init__(self, name):
        self.name = name
        self.axes = []
        self.x_range = [0,0]
        # holds widget refferences of each axis from frame_plot_settings in format: {'figure_name': {'parameter': widget_ref}}
        self.plot_settings = {}
        self.figure_settings = {}
        AddFigure.figure_names.append(name)
        

    def add_ax(self, name, data):
        ax_dict = {
            'name': name,
            'axis_label': name,
            'y_range_max': None,
            'legend_label': name,
            'y_ax_number': 1,
            'color': None,
            'line_width': 1,
            'hide_axis': False,
            'data': data
        }
        self.axes.append(ax_dict)

    def update_axis(self, name, axis_label = None, legend_label = None, y_range_min = None, y_range_max = None, y_ax_number=None, color = None, line_width=None, hide_axis=None):

        for ax in self.axes:
            if ax['name'] == name:
                if axis_label is not None:
                    ax['axis_label'] = axis_label
                if legend_label is not None:
                    ax['legend_label'] = legend_label
                if y_range_min is not [None,""]:
                    ax['y_range_min'] = y_range_min
                if y_range_max is not [None,""]:
                    ax['y_range_max'] = y_range_max
                if y_ax_number is not None:
                    ax['y_ax_number'] = y_ax_number
                if color is not None:
                    ax['color'] = color
                if line_width is not None:
                    ax['line_width'] = line_width
                if line_width is not None:
                    ax['hide_axis'] = hide_axis
                break

    def get_info(self):
        print(self.num_of_axis)

    def get_figure_name(self):
        return self.name

    def sort_by_y_axis_number(self):
        self.axes.sort(key=lambda x: x['y_ax_number'])

    def show_figure(self, preview=False):
        print('***************start plotting****************')
        self.axes.sort(key=lambda x: x['y_ax_number'])
        print('sorted list of axes\n\n')
        
        plt.ioff()  # Turn off interactive mode
        plt.close('all')  # Close all existing figures
        

        """DOPLN PARAMETER GRID KU OSIAM?"""
        legend = []
        labels =[]
                
        # index of the main axis
        used_axes = list(set(int(axis['y_ax_number']) for axis in self.axes))
        print(f'used axes are {used_axes}')       

        # how many axes we need
        number_of_axis = len(used_axes)
        ax = [None] * (number_of_axis+1)
        
        #DOKONCI HIDE AXIS a GRID!!!

        fig, ax[0] = plt.subplots()
        fig.set_size_inches(12, 8)
        
        print('\n\n*********LIMITS CALCULATING**********\n')
        #calculate y limits for each axis
        y_ranges_by_axis = {}
        for index, axis_number in enumerate(used_axes):
            y_range_axis = []
            for axis in self.axes:
                if int(axis['y_ax_number']) == axis_number:
                    print(axis['y_range_min'], axis['y_range_max'])
                    y_range = [axis['y_range_min'], axis['y_range_max']]
                    y_range_axis.append(y_range)
            y_ranges_by_axis[axis_number] = y_range_axis
            
        print(y_ranges_by_axis.items())
        print('\n\n*********END OF LIMITS CALCULATING**********\n')
        

        for index, axis_number in enumerate(used_axes):
            if index > 0:
                ax[index] = ax[0].twinx()  # Create a new y-axis for each subsequent index
           
            for axis in self.axes:
                if int(axis['y_ax_number']) == axis_number:
                    print(f"Plotting on axis {index}: {axis['name']} (y_ax_number: {axis['y_ax_number']})")
                    line, = ax[index].plot(
                        axis['data'].astype(float), 
                        label=axis['axis_label'], 
                        color=axis['color'], 
                        antialiased=True, 
                        linewidth=int(axis['line_width'])
                    )
                    ax[index].set_ylabel(axis['axis_label'])
                    ax[index].spines['right'].set_position(('outward', 60*index))
                    legend.append(line)
                    labels.append(axis['legend_label'])
            
            ax[0].grid(True, which='major', axis='both')

        print('index, axis_index in enumerate(used_axes):')
        for index, axis_index in enumerate(used_axes):
                print(f'index {index} axis_index {axis_index}')
                range_mins = []
                range_maxes = []
                for mins, maxes in y_ranges_by_axis[axis_index]:
                    print(f'mins {mins}, maxes {maxes}')
                    range_mins.append(mins)
                    range_maxes.append(maxes)
                print(min(range_mins), max(range_maxes))
                
                ax[index].set_xlim(self.x_range[0], self.x_range[1])
                ax[index].set_ylim(min(range_mins), max(range_maxes))
        """# Customize the grid
            ax[0].grid(True)  # Turn the grid on

            # Set the major ticks for smaller squares
            ax[0].set_xticks(np.arange(0, 4000, 200))  # Smaller x-ticks, change 0.5 to a smaller value for finer grid
            ax[0].set_yticks(np.arange(-1, 1.1, 0.2))  # Smaller y-ticks, change 0.2 to a smaller value for finer grid

            # Set the minor ticks
            ax[0].set_xticks(np.arange(0, 4000, 10), minor=True)  # Even finer grid on x-axis
            ax[0].set_yticks(np.arange(-1, 1.1, 0.05), minor=True)  # Even finer grid on y-axis

            # Customize the grid lines (Optional)
            ax[0].grid(which='major', color='gray', linestyle='-', linewidth=0.5)
            ax[0].grid(which='minor', color='gray', linestyle=':', linewidth=0.2)"""
        ax[0].legend(legend, labels, loc='upper right', ncol=4)
        
        plt.title(self.name)
        plt.tight_layout()
        plt.ion()
        plt.show()

        


        return
        
        for i, dict in enumerate(self.axes):
            if dict['sep_y']:
                ax2 = ax.twinx()
                line, = ax2.plot(dict['x_value'], dict['value'], label=dict['name'], color=dict['color'], antialiased=True, linewidth=int(dict['line_width']))
                if dict['y_limit'] != None:
                    y_limit_list = ast.literal_eval(dict['y_limit'])
                    ax2.set_ylim(y_limit_list[0], y_limit_list[1])
                ax2.set_ylim(ax2.get_ylim()[0], ax2.get_ylim()[1]*1)
                ax2.spines['right'].set_position(('outward', 60*j))
                ax2.set_ylabel(dict['label'], color=line.get_color())
                ax2.tick_params(axis='y')
                #print(ax2.get_ylim())
                #ax2.grid(True, which='both', axis='y')

                j += 1
            else:
                line, = ax.plot(dict['x_value'], dict['value'], label=dict['name'], color=dict['color'], antialiased=True, linewidth=int(dict['line_width']))
                if dict['y_limit'] != None:
                    y_limit_list = ast.literal_eval(dict['y_limit'])
                    ax.set_ylim(y_limit_list[0], y_limit_list[1])
                #ax.set_ylim(ax.get_ylim()[0], ax.get_ylim()[1])
                #print(ax.get_ylim())
            ax.grid(True, which='major', axis='both')


                    #ax.grid(True)
            if i == 0:
                if dict['color'] == None:
                    dict['color'] = 'red'
                plt.ylabel(dict['label'], color=dict['color'])
            legend.append(line)
            labels.append(dict['label'])

        ax.set_ylim(ax.get_ylim()[0], ax.get_ylim()[1]*1)

        ax.legend(legend, labels, loc='upper right')

        if self.y_limit != None:
            ax.set_ylim(self.y_limit[0], self.y_limit[1])

        plt.title(self.name)
        ax.set_xlabel('x')
        plt.xlabel('x')
        plt.tight_layout()
        plt.ion()
        if plot is True:
            plt.show()
        else:
            return fig
            
    @classmethod
    def change_main_axis(cls, new_main_axis):
        cls.main_axis = new_main_axis

    @classmethod
    def get_main_axis(cls):
        return cls.main_axis

    @classmethod
    def get_all_figure_name(cls):
        return [figure_name for figure_name in cls.figure_names]

if __name__ == '__main__':
    AddFigure.get_all_figure_name()