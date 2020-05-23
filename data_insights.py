'''
Written by Ben McCoy, May 2020

See the README for more detail about the general project.

This script will provide some insights into the operation of the electricity
market of a region within a given date range in the NEM based on data provided
by OpenNEM.

## TODO:
- Histograms of each field
- collect data from clean_data
- add an argument for each plot to save the plot

## Use Case:

Import the class from data_insights.py:
    from data_insights import DataInsights

Set up a DataHandler class object:
    i = DataInisghts()

Collect NEM data a sample set of NEM data:
    i.collect_data()

Plot a scatter plot:
    i.plot_scatter(x='yourfield', y='yourfield', xy_swap=Flase)
    - x and y options include: 'DEMAND', 'PRICE' and more depending on your data collected
    - x must be a single field
    - y can be a single field or list of fields
    - xy_swap=True swaps the x and y values

Plot the average data on a daily or weekly average:
    i.plot_avg(field='yourfield', time_len=yourtime', disp_max=True, disp_demand=False)
    - field options include: 'DEMAND', 'PRICE' and more depending on your data collected
    - time_len options are: 'weeks' and 'days'
    - disp_max=True shows the max of each time unit
    - disp_demand=True shows the average demand in yellow


Plot the data overlaid on a weekly or daily scale:
    i.plot_overlay(field='yourfield', time_len='yourlength')
    - field options include: 'DEMAND', 'PRICE' and more depending on your data collected
    - time_len options are: 'weeks' and 'days'

'''

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.font_manager import FontProperties
import matplotlib.dates as mdates

from data_handler import DataHandler

class DataInsights:
    def __init__(self):
        self.df_5 = pd.DataFrame()
        self.df_5 = pd.DataFrame()

    def collect_data(self):
        DataHandler.collect_data(self)

    def plot_scatter(self, x='PRICE', y='DEMAND', xy_swap=False):
        '''This function creates a scatter plot of the fields given by arguments
        x and y. x is a single field, whereas y can be a single field or a list
        of fields. xy_swap=True swaps the plots x and y axes and allows the x
        axis to have multiple datasets plot.'''

        # Converts y variable to a list if not a list
        if type(y) is not list:
            y = [y]

        # Get the x variable in list form, resamples to 30Min if required
        if x in list(self.df_5):
            x_list = self.df_5[x].resample('30Min', label='right', closed='right').mean().to_list()
        elif x in list(self.df_30):
            x_list = self.df_30[x].to_list()
        else:
            raise DataInsightsError('x does not exist in dataset')

        # Get the y variables in list form, sotred in a list, resamples to
        # 30Min if required
        y_list = []
        for item in y:
            if item in list(self.df_5):
                y_list.append(self.df_5[item].resample('30Min', label='right', closed='right').mean().to_list())
            elif item in list(self.df_30):
                y_list.append(self.df_30[item].to_list())
            else:
                raise DataInsightsError('y does not exist in dataset')

        # Make sure x and y are the same length
        for item in y_list:
            if len(x_list) != len(item):
                raise DataInsightsError('x and y are not same len, check your data!')

        # Make the plot and set title and labels, swaps x and y if xy_swap=True
        if xy_swap == False:
            for i in range(len(y_list)):
                plt.scatter(x=x_list, y=y_list[i], label=y[i])
                plt.xlabel(x)

        # swaps the x and y values
        else:
            y_temp = x_list
            x_list = y_list
            y_list = y_temp

            for i in range(len(x_list)):
                plt.scatter(x=x_list[i], y=y_list, label=y[i])
                plt.ylabel(x)

        # Set the plot settings
        plt.title('A scatter plot of items in the legend')
        plt.legend()
        plt.show()

    def plot_avg(self, field='DEMAND', time_len='weeks', disp_max=True, disp_demand=False):
        '''This function takes a field and time_len and plots the average
        profile for the given time_len, as well as the max, min and standard
        deviation from mean on the same axis.'''

        # Check that the given time_len is valid
        if time_len not in ['weeks', 'days']:
            raise DataInsightsError("time_len must be 'days' or 'weeks'")

        # Create a temporary pandas series to resample data if required. Also
        # acts as a check that the field given to function is valid
        if field in list(self.df_5):
            temp_df = self.df_5[field].resample('30Min', label='right', closed='right').mean()
        elif field in list(self.df_30):
            temp_df = self.df_30[field]
        else:
            raise DataInsightsError('Field not in dataset')

        # Resample demand
        if disp_demand == True:
            demand = self.df_5['DEMAND'].resample('30Min', label='right', closed='right').mean()

        # Create a temporary empty dataframe to host the relevant data
        columns = ['Mean', 'SD', 'Min', 'Max']
        plot_df = pd.DataFrame(columns=columns)

        # Get the mean, std, min and max for each 30 min interval in the week
        # also add a new column to be used for the index later
        if time_len == 'weeks':
            plot_df['Mean'] = temp_df.groupby([temp_df.index.weekday, temp_df.index.hour, temp_df.index.minute]).mean()
            plot_df['SD'] = temp_df.groupby([temp_df.index.weekday, temp_df.index.hour, temp_df.index.minute]).std()
            plot_df['Min'] = temp_df.groupby([temp_df.index.weekday, temp_df.index.hour, temp_df.index.minute]).min()
            if disp_max == True:
                plot_df['Max'] = temp_df.groupby([temp_df.index.weekday, temp_df.index.hour, temp_df.index.minute]).max()
            plot_df['Hour'] = self.gen_date('weeks')

            # Display demand
            if disp_demand == True:
                plot_df['Demand'] = demand.groupby([demand.index.weekday, demand.index.hour, demand.index.minute]).mean()

        # Get the mean, std, min and max for each 30 min interval in the day
        # also add a new column to be used for the index later
        if time_len == 'days':
            plot_df['Mean'] = temp_df.groupby([temp_df.index.hour, temp_df.index.minute]).mean()
            plot_df['SD'] = temp_df.groupby([temp_df.index.hour, temp_df.index.minute]).std()
            if disp_max == True:
                plot_df['Max'] = temp_df.groupby([temp_df.index.hour, temp_df.index.minute]).max()
            plot_df['Min'] = temp_df.groupby([temp_df.index.hour, temp_df.index.minute]).min()
            plot_df['Hour'] = self.gen_date('days')

            # Display demand
            if disp_demand == True:
                plot_df['Demand'] = demand.groupby([demand.index.hour, demand.index.minute]).mean()

        # Reset the index to the 'Hours' column
        plot_df.set_index('Hour', inplace=True)

        # Plot the mean, min, max and fill the gaps between mean+SD and mean-SD
        plt.plot(plot_df['Mean'], 'k-', label='Mean')
        plt.fill_between(plot_df.index, plot_df['Mean']-plot_df['SD'], plot_df['Mean']+plot_df['SD'])
        plt.plot(plot_df['Min'], label='Min', c='g')
        plt.plot(plot_df['Max'], label='Max', c='r')

        # Display demand
        if disp_demand == True:
            plt.plot(plot_df['Demand'], label='Average Demand', c='y')

        if time_len == 'weeks':
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            plt.gca().xaxis.set_major_locator(mdates.DayLocator())

        # adjust the settings for the plot
        plt.xlabel('DateTime')
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
            temp_df = self.df_5[field].resample('30Min', label='right', closed='right').mean()
        elif field in list(self.df_30):
            temp_df = self.df_30[field]
        else:
            raise DataInsightsError('Field not in dataset')

        # Split the data into a list of weeks
        if time_len == 'days':
            weeks = [g for n, g in temp_df.groupby(pd.Grouper(freq='D'))]
        else:
            weeks = [g for n, g in temp_df.groupby(pd.Grouper(freq='W'))]
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

    def gen_date(self, time_len):
        '''A simple function to generate a datetime for the plot_avg() function
        depending on if the time_len is 'days' or 'weeks'. '''

        if time_len == 'days':
            time_fixed = []
            times = pd.date_range('2000-01-01', periods=48, freq='30Min')
            for time in times:
                time_fixed.append(time.time())

        if time_len == 'weeks':
            time_fixed = []
            times = pd.date_range('2000-01-01', periods=336, freq='30Min')
            for time in times:
                time_fixed.append(time)
        return time_fixed

class DataInsightsError(Exception):
    pass

if __name__ == "__main__":
    main()
