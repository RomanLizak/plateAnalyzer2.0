import matplotlib.pyplot as plt
import ast

class AddFigure():
    main_axis = 1
    figure_names = []
    color_list = ["red", "blue", "green", "orange", "purple", "brown", "pink", "gray"]

    def __init__(self, name):
        self.name = name
        self.axes = []
        # holds widget refferences of each axis from frame_plot_settings in format: {'figure_name': {'parameter': widget_ref}}
        self.plot_settings = {}
        AddFigure.figure_names.append(name)
        

    def add_ax(self, name, data):
        ax_dict = {
            'name': name,
            'axis_label': name,
            'x_limit': None,
            'y_limit': None,
            'legend_label': name,
            'y_ax_number': 1,
            'color': None,
            'line_width': 1,
            'hide_axis': False,
            'data': data
        }
        self.axes.append(ax_dict)

    def update_axis(self, name, axis_label = None, legend_label = None, x_limit=None, y_limit = None, y_ax_number=None, color = None, line_width=None, hide_axis=None):

        for ax in self.axes:
            for ax in self.axes:
                if ax['name'] == name:
                    if axis_label is not None:
                        ax['axis_label'] = axis_label
                    if legend_label is not None:
                        ax['legend_label'] = legend_label
                    if x_limit is not None:
                        ax['x_limit'] = x_limit
                    if y_limit is not None:
                        ax['y_limit'] = y_limit
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
        
        #self.axes.sort(key=lambda x: x['y_ax_number'])
        
        print(self.name)
        for ax in self.axes:
            print(ax['name'])
        
        return
        plt.ioff()  # Turn off interactive mode
        plt.close('all')  # Close all existing figures
        fig, ax = plt.subplots()
        fig.set_size_inches(12, 8)

        legend = []
        labels =[]

        # main axis first
        for index, axis in self.axes:
            if cls.main_axis == axis.y_ax_number:
                line, = ax.plot(dict['x_value'], dict['value'], label=dict['name'], color=dict['color'], antialiased=True, linewidth=int(dict['line_width']))
                if dict['y_limit'] != None:
                    y_limit_list = ast.literal_eval(dict['y_limit'])
                    ax.set_ylim(y_limit_list[0], y_limit_list[1])
        
        # all other axes
        for index, axis in self.axes:
            if cls.main_axis != axis.y_ax_number:
                j=1

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