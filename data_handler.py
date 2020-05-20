'''
Written by Ben McCoy, May 2020

See the README for more detail about the general project.

This script contains a class object that can:
- Use the opennempy web_api module to collect NEM data from the OpenNem api
- Perform checks and verification of the data
- Present the important stats of the data (mean, std, min/max, count, sum)
- Organise and store the data in CSVs locally (this will be done using
  opennempy's load_data() as it works really well already)
- Open the data from local storage (this will be done using opennempy's
  load_data() as it works really well already)
- Replace any null or missing values through interpolation, medians or
  weekly/daily averages

## TODO:
- Add a function to replace bad/missing data through: daily/weekly average of
    the value.
- Figure out what to do when two or more NaNs appear in consecutively.
- Make a check for d_end being before d_start.
- In data_checks, print what percentage of data is null values.
- Remove anomalies

## Nice to have:
- replace_null function could be able take columns as an argument so that
    different columns have different methods of replacing null data.

## Use Case:

Import the class from data_collect.py:
    from data_collect import DataHandler

Set up a DataHandler class object:
    test = DataHandler()

Collect NEM data:
    test.collect_data(d_start=(yyyy,m,d), d_end=(yyyy,m,d), region='reg1')
    - regions include: 'sa1', 'nsw1', 'vic1', 'tas1', 'qld1'

Print the data:
    test.print_data(res=5)
    - res options include: 5, 30

Plot the data:
    test.plot_data()

Run checks on the data:
    test.data_checks()

Get some general information about the data:
    test.data_stats(print_op=True)

Replace any null values in the data:
    test.replace_null(method='yourmethod')
    - methods include: 'median', 'interpolate'

'''

from opennempy import web_api
import datetime
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import numpy as np


class DataHandler:
    def __init__(self):
        self.df_5 = pd.DataFrame()
        self.df_30 = pd.DataFrame()
        self.df_stats = pd.DataFrame()

    def print_data(self, res=5):
        '''Prints the data in short form for a given resolution'''

        if res == 5:
            print(self.df_5)
        if res == 30:
            print(self.df_30)

    def plot_data(self):
        '''Plots the data on two subplots, if the data exists.'''

        if self.df_5.empty == False and self.df_30.empty == False:

            # Set font size to extra small to better fit the legend
            fontP = FontProperties()
            fontP.set_size('x-small')

            # Create plot figure with two subplots
            fig, axs = plt.subplots(2)

            # Set up the 5 min resolution plot
            axs[0].plot(self.df_5)
            axs[0].set_title('Demand (MW) and Generation (MW) in 5 Minute Resolution')
            axs[0].legend(list(self.df_5), loc='upper center',
                        bbox_to_anchor=(0.5,1), fancybox=True,
                        ncol=int(len(list(self.df_5))/2)+1, prop=fontP)

            # Set up the 30 min resolution plot
            axs[1].plot(self.df_30)
            axs[1].set_title('Price ($/MW), Temperature (Deg C) and Rooftop Solar Generation (MW) in 30 Minute Resolution')
            axs[1].legend(list(self.df_30), loc='upper center',
                        bbox_to_anchor=(0.5,1), fancybox=True,
                        ncol=len(list(self.df_30)), prop=fontP)

            # Rotate the x labels for better fit
            plt.setp(axs[0].get_xticklabels(), rotation=30, horizontalalignment='right')
            plt.setp(axs[1].get_xticklabels(), rotation=30, horizontalalignment='right')
            fig.tight_layout(h_pad=1)

            plt.show()

    def collect_data(self, d_start=(2019,1,1), d_end=(2019,2,1), region='sa1', print_op=False, dropna=True):
        '''This function takes a start dates as a tuple, a end date as a tupe, a
        region as a string and print_op as a boolean. The defaults are to take
        data from the 1/1/2018 to 12/12/2019 from SA. The function downloads 5 and
        30 minute data using the web_api from opennempy, between the d_start and
        d_end ranges from the region given. If the print_op variable is given as
        True, then the data is printed after being downloaded. If any errors occur,
        an exception is raised with DataHandlerError.'''

        # Check region exsits
        if region not in ['nsw1', 'qld1', 'sa1','tas1','vic1']:
            raise DataHandlerError('Region must be one of nsw1, qld1, sa1, tas1, vic1')

        # Check that dates given are correct format
        try:
            d1 = datetime.datetime(d_start[0], d_start[1], d_start[2])
            d2 = datetime.datetime(d_end[0], d_end[1], d_end[2])
        except:
            raise DataHandlerError('Issue with the input dates')

        print('- Collecting data from OpenNEM web_api with properties:')
        print('- Start date: \t' + str(d_start))
        print('- End date: \t' + str(d_end))
        print('- Region: \t' + convert_region_to_string(region))

        # Attempt to download using web_api.load_data(), if there is an issue
        # it raises a DataHandlerError
        try:
            self.df_5, self.df_30 = web_api.load_data(d1=d1, d2=d2, region=region)
        except:
            raise DataHandlerError('Issue occurred during download')

        # Removes nan columns and prints removed columns
        if dropna:
            prev_all_cols = list(self.df_5) + list(self.df_30)
            self.df_5.dropna(axis=1, how='all', inplace=True)
            self.df_30.dropna(axis=1, how='all', inplace=True)
            new_all_cols = list(self.df_5) + list(self.df_30)
            rem_cols = [x for x in prev_all_cols if x not in new_all_cols]
            print('- Removed Columns: ', rem_cols)

        # Prints the data
        if print_op == True:
            print(self.df_5, self.df_30)

    def data_checks(self):
        '''Checks the 5 minute and 30 minute data for any null values and prints
        the rows of the pandas that have null values present. Also prints the
        dtypes of each column for user to check incase there are inconsistencies.'''

        print('- Performing checks on 5 minute resolved data:')
        # Checks for any cells with null value and prints all rows with null
        if self.df_5.isnull().sum().sum() > 0:
            print('- Found the below missing data:')
            print(self.df_5[self.df_5.isnull().any(axis=1)])
        else:
            print('No NaN or empty values')
        print('- The types of values in each column are:')
        # Prints they data types of each column
        print(self.df_5.dtypes)


        print('- Performing checks on 30 minute resolved data:')
        # Checks for any cells with null value and prints all rows with null
        if self.df_30.isnull().sum().sum() > 0:
            print('- Found the below missing data:')
            print(self.df_30[self.df_30.isnull().any(axis=1)])
        else:
            print('No NaN or empty values')
        print('- The types of values in each column are:')
        # Prints they data types of each column
        print(self.df_30.dtypes)

    def data_stats(self, print_op=True):
        '''This function creates a table for each dataset with the following
        stats for each field: mean, standard deviation, median, minimum,
        maximum, length, total'''

        # Create a pandas DF with the stats for the 30 min resolved data
        df_30_index = list(self.df_30)
        df_30_temp = pd.DataFrame(index=df_30_index)
        df_30_temp['Mean'] = self.df_30.mean()
        df_30_temp['Std'] = self.df_30.std()
        df_30_temp['Median'] = self.df_30.median()
        df_30_temp['Min'] = self.df_30.min()
        df_30_temp['Max'] = self.df_30.max()
        df_30_temp['Count'] = self.df_30.count()
        df_30_temp['Sum'] = self.df_30.sum()

        # Create a pandas DF with the stats for the 5 min resolved data
        df_5_index = list(self.df_5)
        df_5_temp = pd.DataFrame(index=df_5_index)
        df_5_temp['Mean'] = self.df_5.mean()
        df_5_temp['Std'] = self.df_5.std()
        df_5_temp['Median'] = self.df_5.median()
        df_5_temp['Min'] = self.df_5.min()
        df_5_temp['Max'] = self.df_5.max()
        df_5_temp['Count'] = self.df_5.count()
        df_5_temp['Sum'] = self.df_5.sum()

        # combine the two stat DFs
        self.df_stats = pd.concat([df_5_temp, df_30_temp])

        # Print the DF
        if print_op == True:
            print(self.df_stats)

    def replace_null(self, method='interpolate'):
        '''Replaces any NaN or missing values using one of the methods out of
        median, interpolate, daily_avg or weekly_avg'''

        # Check that the method given is correct
        methods = ['median', 'interpolate', 'daily_avg', 'weekly_avg']
        if method not in methods:
            raise DataHandlerError('Method must be one of: median, interpolate, daily_avg, weekly_avg')

        if method == 'median':
            # Get a dict of the median values for each column
            df_5_med_dict = self.df_5.median().to_dict()
            df_30_med_dict = self.df_30.median().to_dict()

            # Fill the null values with median values
            self.df_5.fillna(value=df_5_med_dict, inplace=True)
            self.df_30.fillna(value=df_30_med_dict, inplace=True)

        if method == 'interpolate':
            # Get the first and last indexes for each dataset
            df_30_ends = []
            df_5_ends = []
            df_30_ends.append(self.df_30.first_valid_index())
            df_30_ends.append(self.df_30.last_valid_index())
            df_5_ends.append(self.df_5.first_valid_index())
            df_5_ends.append(self.df_5.last_valid_index())

            # Get the fields for each dataset
            df_30_fields = list(self.df_30)
            df_5_fields = list(self.df_5)

            # Init the dicts that will contain the field and indexes of null values
            df_30_null_dict = {}
            df_5_null_dict = {}

            # Populate the null_dicts
            for i in df_30_fields:
                df_30_null_dict[i] = self.df_30[self.df_30[i].isnull()].index.tolist()
            for i in df_5_fields:
                df_5_null_dict[i] = self.df_5[self.df_5[i].isnull()].index.tolist()

            # Iterate through the null_dict key-value pairs and replace the
            # null values
            for k, v in df_30_null_dict.items():
                for i in v:
                    if i not in df_30_ends:
                        self.interpolate_normal(k, i, 'df_30')
                    else:
                        self.interpolate_ends(k, i, 'df_30', df_30_ends.index(i))

            for k, v in df_5_null_dict.items():
                for i in v:
                    if i not in df_5_ends:
                        self.interpolate_normal(k, i, 'df_5')
                    else:
                        self.interpolate_ends(k, i, 'df_5', df_5_ends.index(i))

        if method == 'daily_avg':

            df_5_mean = self.df_5.groupby([self.df_5.index.hour, self.df_5.index.minute]).mean()
            df_30_mean = self.df_30.groupby([self.df_30.index.hour, self.df_30.index.minute]).mean()

            df_30_mean.index = ['{}_{}'.format(i, j) for i, j in df_30_mean.index]
            df_5_mean.index = ['{}_{}'.format(i, j) for i, j in df_5_mean.index]

            # Init the dicts that will contain the field and indexes of null values
            df_30_null_dict = {}
            df_5_null_dict = {}

            # Populate the null_dicts
            for i in list(self.df_30):
                df_30_null_dict[i] = self.df_30[self.df_30[i].isnull()].index.tolist()
            for i in list(self.df_5):
                df_5_null_dict[i] = self.df_5[self.df_5[i].isnull()].index.tolist()

            for k, v in df_30_null_dict.items():
                for i in v:
                    hour = str(i).replace(' ', ':').split(':')[1]
                    minute = str(i).replace(' ', ':').split(':')[2]
                    mean_index = str(int(hour)) + '_' + str(int(minute))
                    self.df_30.at[i, k] = df_30_mean[k][mean_index]

            for k, v in df_5_null_dict.items():
                for i in v:
                    hour = str(i).replace(' ', ':').split(':')[1]
                    minute = str(i).replace(' ', ':').split(':')[2]
                    mean_index = str(int(hour)) + '_' + str(int(minute))
                    self.df_5.at[i, k] = df_5_mean[k][mean_index]

        if method == 'weekly_avg':

            df_5_mean = self.df_5.groupby([self.df_5.index.weekday, self.df_5.index.hour, self.df_5.index.minute]).mean()
            df_30_mean = self.df_30.groupby([self.df_30.index.weekday, self.df_30.index.hour, self.df_30.index.minute]).mean()

            df_30_mean.index = ['{}_{}_{}'.format(i, j, k) for i, j, k in df_30_mean.index]
            df_5_mean.index = ['{}_{}_{}'.format(i, j, k) for i, j, k in df_5_mean.index]

            print(df_30_mean)
            print(df_5_mean)

            # Init the dicts that will contain the field and indexes of null values
            df_30_null_dict = {}
            df_5_null_dict = {}

            # Populate the null_dicts
            for i in list(self.df_30):
                df_30_null_dict[i] = self.df_30[self.df_30[i].isnull()].index.tolist()
            for i in list(self.df_5):
                df_5_null_dict[i] = self.df_5[self.df_5[i].isnull()].index.tolist()

            # print(df_30_null_dict)
            # print(df_5_null_dict)

            for k, v in df_30_null_dict.items():
                for i in v:
                    day = i.weekday()
                    hour = str(i).replace(' ', ':').split(':')[1]
                    minute = str(i).replace(' ', ':').split(':')[2]
                    mean_index = str(day) + '_' + str(int(hour)) + '_' + str(int(minute))
                    self.df_30.at[i, k] = df_30_mean[k][mean_index]

            for k, v in df_5_null_dict.items():
                for i in v:
                    day = i.weekday()
                    hour = str(i).replace(' ', ':').split(':')[1]
                    minute = str(i).replace(' ', ':').split(':')[2]
                    mean_index = str(day) + '_' + str(int(hour)) + '_' + str(int(minute))
                    self.df_5.at[i, k] = df_5_mean[k][mean_index]

    def interpolate_normal(self, k, i, df_name):
        '''This function takes a data field as k, and an index value as i, as
        well as the name of a DataFrame as df_name. It finds the numerical index
        of the index i and then the previous and next values in column k of
        index i and determines the mean. The value for column k, index i is then
        set to the mean value of the next and previous values.'''

        if df_name == 'df_30':
            loc = self.df_30.index.get_loc(i)
            prev = self.df_30.iloc[loc-1][k]
            next = self.df_30.iloc[loc+1][k]
            mean = (prev + next) * 0.5
            self.df_30.at[i, k] = mean

        elif df_name == 'df_5':
            loc = self.df_5.index.get_loc(i)
            prev = self.df_5.iloc[loc-1][k]
            next = self.df_5.iloc[loc+1][k]
            mean = (prev + next) * 0.5
            self.df_5.at[i, k] = mean

    def interpolate_ends(self, k, i, df_name, end_index):
        '''This function acts as interpolate_normal, except that the missing
        value is either at the first or last index of the dataframe. as such, it
        takes the next or previous value and replaces the NaN value, depending
        on if the first or last value is missing.'''

        if df_name == 'df_30':
            if end_index == 0:
                loc = self.df_30.index.get_loc(i)
                next = self.df_30.iloc[loc+1][k]
                self.df_30.at[i, k] = next
            else:
                loc = self.df_30.index.get_loc(i)
                prev = self.df_30.iloc[loc-1][k]
                self.df_30.at[i, k] = prev

        if df_name == 'df_5':
            if end_index == 0:
                loc = self.df_5.index.get_loc(i)
                next = self.df_5.iloc[loc+1][k]
                self.df_5.at[i, k] = next
            else:
                loc = self.df_5.index.get_loc(i)
                prev = self.df_5.iloc[loc-1][k]
                self.df_5.at[i, k] = prev


class DataHandlerError(Exception):
    pass

def convert_region_to_string(region):
    ''' Basic elper function to convert region abrevitations to full names'''

    if region == 'sa1':
        return_region = 'South Australia'
    elif region == 'nsw1':
        return_region = 'New South Wales'
    elif region == 'qld1':
        return_region = 'Queensland'
    elif region == 'tas1':
        return_region = 'Tasmania'
    elif region == 'vic1':
        return_region = 'Victoria'
    else:
        return_region = 'No region given'

    return return_region

if __name__ == "__main__":
    main()
