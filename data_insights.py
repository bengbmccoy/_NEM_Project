'''
Written by Ben McCoy, May 2020

See the README for more detail about the general project.

This script will provide some insights into the operation of the electricity
market of a region within a given date range in the NEM based on data provided
by OpenNEM.



'''

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.font_manager import FontProperties

from data_handler import DataHandler

class DataInsights:
    def __init__(self):
        self.df_5 = pd.DataFrame()
        self.df_5 = pd.DataFrame()
        self.temp_df = pd.DataFrame()
        self.plot_df = pd.DataFrame()

    def collect_data(self):
        DataHandler.collect_data(self)

    def plot_weeks(self, field='DEMAND'):
        '''This function takes a field of the data as input, splits the data
        into week-long segments and plots each week-long segment onto the same
        axis'''

        # Create a temporary pandas series to resample data if required. Also
        # acts as a check that the field given to function is valid
        if field in list(self.df_5):
            self.temp_df = self.df_5[field].resample('30Min', label='right', closed='right').mean()
        elif field in list(self.df_30):
            self.temp_df = self.df_30[field]
        else:
            raise DataInsightsError('Field not in dataset')

        # Split the data into a list of weeks
        weeks = [g for n, g in self.temp_df.groupby(pd.Grouper(freq='W'))]

        # Init the lists used to plot and label the data
        indexes, y_data, labels = [], [], []

        # iterate through weeks of data and fill the init lists above
        for week in weeks:
            first = str(week.first_valid_index()).split(' ')[0]
            last = str(week.last_valid_index()).split(' ')[0]
            labels.append(str(first) + ' ' + str(last))
            week_index = []
            week_data = []
            for index, row in week.iteritems():
                week_index.append((index.dayofweek*24) + index.hour + (index.minute/60))
                week_data.append(row)
            indexes.append(week_index)
            y_data.append(week_data)

        # iterate through the lists of data/labels and plot each
        for j in range(len(labels)):
            plt.plot(indexes[j], y_data[j], label=labels[j])

        # adjust the settings for the plot
        plt.xlabel('Hours since midnight Sunday')
        plt.ylabel(str(field))
        plt.title('A plot of the data broken into weeks and overlayed on the same axis')
        fontP = FontProperties()
        fontP.set_size('x-small')
        plt.legend(loc='upper right', fancybox=True, prop=fontP, ncol=int(len(labels)/2))
        plt.show()

class DataInsightsError(Exception):
    pass

if __name__ == "__main__":
    main()
