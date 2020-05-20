'''
Written by Ben McCoy, May 2020

See the README for more detail about the general project.

This script will provide some insights into the operation of the electricity
market of a region within a given date range in the NEM based on data provided
by OpenNEM.

## TODO:
- Remove the self.temp_df and self.plot_df variable when no longer needed during
    prototyping
- Fix the x axis for plot_avg and plot_overlay. Also Set the scale to end so that
    there is no whitespace on the plots

## Use Case:

Import the class from data_insights.py:
    from data_insights import DataInsights

Set up a DataHandler class object:
    i = DataInisghts()

Collect NEM data a sample set of NEM data:
    i.collect_data()

Plot the data overlaid on a weekly or daily scale:
    i.plot(field='yourfield', time_len='yourlength')
    - field options include: 'DEMAND', 'PRICE' and more depending on your data collected
    - time_len options are: 'weeks' and 'days'

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

    def plot_avg(self, field='DEMAND', time_len='weeks'):
        '''This function takes a field and time_len and plots the average
        profile for the given time_len, as well as the max, min and standard
        deviation from mean on the same axis.'''

        # Check that the given time_len is valid
        if time_len not in ['weeks', 'days']:
            raise DataInsightsError("time_len must be 'days' or 'weeks'")

        # Create a temporary pandas series to resample data if required. Also
        # acts as a check that the field given to function is valid
        if field in list(self.df_5):
            self.temp_df = self.df_5[field].resample('30Min', label='right', closed='right').mean()
        elif field in list(self.df_30):
            self.temp_df = self.df_30[field]
        else:
            raise DataInsightsError('Field not in dataset')

        # Create a temporary empty dataframe to host the relevant data
        columns = ['Mean', 'SD', 'Min', 'Max']
        self.plot_df = pd.DataFrame(columns=columns)

        # Get the mean, std, min and max for each 30 min interval in the week
        # also add a new column to be used for the index later
        if time_len == 'weeks':
            self.plot_df['Mean'] = self.temp_df.groupby([self.temp_df.index.weekday, self.temp_df.index.hour, self.temp_df.index.minute]).mean()
            self.plot_df['SD'] = self.temp_df.groupby([self.temp_df.index.weekday, self.temp_df.index.hour, self.temp_df.index.minute]).std()
            self.plot_df['Min'] = self.temp_df.groupby([self.temp_df.index.weekday, self.temp_df.index.hour, self.temp_df.index.minute]).min()
            self.plot_df['Max'] = self.temp_df.groupby([self.temp_df.index.weekday, self.temp_df.index.hour, self.temp_df.index.minute]).max()
            self.plot_df['Hour'] = np.arange(0.0, 168.0, 0.5)

        # Get the mean, std, min and max for each 30 min interval in the day
        # also add a new column to be used for the index later
        if time_len == 'days':
            self.plot_df['Mean'] = self.temp_df.groupby([self.temp_df.index.hour, self.temp_df.index.minute]).mean()
            self.plot_df['SD'] = self.temp_df.groupby([self.temp_df.index.hour, self.temp_df.index.minute]).std()
            self.plot_df['Max'] = self.temp_df.groupby([self.temp_df.index.hour, self.temp_df.index.minute]).max()
            self.plot_df['Min'] = self.temp_df.groupby([self.temp_df.index.hour, self.temp_df.index.minute]).min()
            self.plot_df['Hour'] = np.arange(0.0, 24.0, 0.5)

        # Reset the index to the 'Hours' column
        self.plot_df.set_index('Hour', inplace=True)

        # Plot the mean, min, max and fill the gaps between mean+SD and mean-SD
        plt.plot(self.plot_df['Mean'], 'k-', label='Mean')
        plt.fill_between(self.plot_df.index, self.plot_df['Mean']-self.plot_df['SD'], self.plot_df['Mean']+self.plot_df['SD'])
        plt.plot(self.plot_df['Min'], label='Min', c='g')
        plt.plot(self.plot_df['Max'], label='Max', c='r')

        # adjust the settings for the plot
        plt.xlabel('Hours since midnight Sunday')
        plt.ylabel(str(field))
        plt.title('A plot of the hourly average data')
        fontP = FontProperties()
        fontP.set_size('x-small')
        plt.legend(loc='upper right', fancybox=True, prop=fontP)
        plt.show()

    def plot_overlay(self, field='DEMAND', time_len='weeks'):
        '''This function takes a field of the data and the time length being
        plotted as input, splits the data into week-long segments and plots each
        week-long segment onto the same axis.'''

        # Check that the given time_len is valid
        if time_len not in ['weeks', 'days']:
            raise DataInsightsError("time_len must be 'days' or 'weeks'")

        # Create a temporary pandas series to resample data if required. Also
        # acts as a check that the field given to function is valid
        if field in list(self.df_5):
            self.temp_df = self.df_5[field].resample('30Min', label='right', closed='right').mean()
        elif field in list(self.df_30):
            self.temp_df = self.df_30[field]
        else:
            raise DataInsightsError('Field not in dataset')

        # Split the data into a list of weeks
        if time_len == 'days':
            weeks = [g for n, g in self.temp_df.groupby(pd.Grouper(freq='D'))]
        else:
            weeks = [g for n, g in self.temp_df.groupby(pd.Grouper(freq='W'))]
        # Init the lists used to plot and label the data
        indexes, y_data, labels = [], [], []

        # iterate through weeks of data and fill the init lists  above
        for week in weeks:
            first = str(week.first_valid_index()).split(' ')[0]
            last = str(week.last_valid_index()).split(' ')[0]
            labels.append(str(first) + ' ' + str(last))
            week_index = []
            week_data = []
            for index, row in week.iteritems():
                if time_len == 'days':
                    week_index.append(index.hour + (index.minute/60))
                else:
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
        plt.title('A plot of the data broken into ' + str(time_len) + ' and overlayed on the same axis')
        fontP = FontProperties()
        fontP.set_size('x-small')
        plt.legend(loc='upper right', fancybox=True, prop=fontP)
        plt.show()

class DataInsightsError(Exception):
    pass

if __name__ == "__main__":
    main()
