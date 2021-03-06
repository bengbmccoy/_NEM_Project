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
- Write tests for new mthods and functions
- Remove anomalies
- Make sure all the date formats used in script are consistent

## Nice to have:
- Make a check for d_end being before d_start.

## Use Case:

Import the class from data_collect.py:
    from data_collect import DataHandler

Set up a DataHandler class object:
    h = DataHandler()

Collect NEM data:
    h.collect_data(d_start=(yyyy,m,d), d_end=(yyyy,m,d), region='reg1')
    - regions include: 'sa1', 'nsw1', 'vic1', 'tas1', 'qld1'
    - To download the data with no NaNs for all states except vic from 2018 and 2019:
    -- h.collect_data(d_start=['2018-01-01', '2019-02-18', '2019-10-28'], d_end=['2019-02-10', '2019-10-20', '2020-01-01'])

Print the data:
    h.print_data(res=5)
    - res options include: 5, 30

Plot the data:
    h.plot_data()

Make a boxplot of a field or fields:
    h.boxplot(field='yourfield')
    - field options include: all (attempts to plot all fields in box diagram)
        or any other field in hte dataset

Run checks on the data:
    h.data_checks()

Get some general information about the data:
    h.data_stats(print_op=True)

Replace any null values in the data:
    h.replace_null(method='yourmethod')
    - methods include: 'median', 'interpolate', 'daily_avg', 'weekly_avg'

'''

from opennempy import web_api
import datetime
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import numpy as np
import seaborn as sns


class DataHandler:
    def __init__(self):
        self.df_5 = pd.DataFrame()
        self.df_30 = pd.DataFrame()
        self.df_stats = pd.DataFrame()
        self.date_df = pd.DataFrame()

    def collect_data(self, d_start='2019-01-01', d_end='2019-02-01', region='sa1',
                    print_op=False, dropna=True):
        '''This function takes a start dates as a tuple, a end date as a tupe, a
        region as a string and print_op as a boolean. The defaults are to take
        data from the 1/1/2018 to 12/12/2019 from SA. The function downloads 5 and
        30 minute data using the web_api from opennempy, between the d_start and
        d_end ranges from the region given. If the print_op variable is given as
        True, then the data is printed after being downloaded. If any errors occur,
        an exception is raised with DataHandlerError.'''

        # Reset the DFs
        self.df_5 = pd.DataFrame()
        self.df_30 = pd.DataFrame()

        # Check region exsits
        if region not in ['nsw1', 'qld1', 'sa1','tas1','vic1']:
            raise DataHandlerError('Region must be one of nsw1, qld1, sa1, tas1, vic1')

        # Converts date variables to a list if not a list
        if type(d_start) is not list:
            d_start = [d_start]
        if type(d_end) is not list:
            d_end = [d_end]

        # Check an equal number of d_starts and d_ends were given
        if len(d_start) != len(d_end):
            raise DataHandlerError('Different number of dates given as input')

        for i in range(len(d_start)):
            # Split the dates into a list of [yyyy, mm, dd]
            date1 = d_start[i].split('-')
            date2 = d_end[i].split('-')

            # Check that dates given are correct format
            try:
                d1 = datetime.datetime(int(date1[0]), int(date1[1]), int(date1[2]))
                d2 = datetime.datetime(int(date2[0]), int(date2[1]), int(date2[2]))
            except:
                raise DataHandlerError('Issue with the input dates')

            if print_op == True:
                print('- Collecting data from OpenNEM web_api with properties:')
                print('- Start date: \t' + str(date1))
                print('- End date: \t' + str(date2))
                print('- Region: \t' + convert_region_to_string(region))

            # Attempt to download using web_api.load_data(), if there is an issue
            # it raises a DataHandlerError
            try:
                temp_df_5, temp_df_30 = web_api.load_data(d1=d1, d2=d2, region=region)
            except:
                raise DataHandlerError('Issue occurred during download')

            self.df_5 = self.df_5.append(temp_df_5)
            self.df_30 = self.df_30.append(temp_df_30)

        # Removes columns that are only NaN values and prints removed columns
        if dropna:
            prev_all_cols = list(self.df_5) + list(self.df_30)
            self.df_5.dropna(axis=1, how='all', inplace=True)
            self.df_30.dropna(axis=1, how='all', inplace=True)
            new_all_cols = list(self.df_5) + list(self.df_30)
            rem_cols = [x for x in prev_all_cols if x not in new_all_cols]
            if print_op == True:
                print('- Removed Columns: ', rem_cols)

        # Prints the data
        if print_op == True:
            print(self.df_5, self.df_30)

    def save_clean_data(self, fname):
        '''This function takes a filename as an argument and then combines the
        dataframes into one 30_min reslved dataframe and saves the new dataFrame
        to the clean_data folder to be used for inisghts and model training.'''

        # Resample df_30 and then concat the DFs together.
        save_5_df = self.df_5.resample('30Min', label='right', closed='right').mean()
        save_30_df = self.df_30
        save_df = pd.concat([save_5_df, save_30_df], axis=1, sort=False)

        # Removes any rows with NaN values still present
        save_df.dropna(inplace=True)

        # Save the DF
        fname = 'clean_data/' + fname
        save_df.to_csv(fname)

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

    def boxplot(self, field='PRICE'):
        '''This function takes a list or single element as the fields and makes
        a box plot for each of the fields given.'''

        # Gets a list of all fields in the 5min and 30min datasets
        if field == 'all':
            field = list(self.df_5) + list(self.df_30)

        # Converts y variable to a list if not a list
        if type(field) is not list:
            field = [field]

        # If there is only one plot to be made
        if len(field) == 1:
            if field[0] in list(self.df_5):
                sns.boxplot(x=self.df_5[field[0]])
            elif field[0] in list(self.df_30):
                sns.boxplot(x=self.df_30[field[0]])
            plt.show()

        # If there are multiple plots to be made
        else:
            fig, axs = plt.subplots(len(field))
            for i in range(len(field)):
                if field[i] in list(self.df_5):
                    sns.boxplot(x=self.df_5[field[i]], ax=axs[i])
                elif field[i] in list(self.df_30):
                    sns.boxplot(x=self.df_30[field[i]], ax=axs[i])
            fig.tight_layout()
            plt.show()

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
        df_30_temp['Percent NaN'] = self.df_30.isnull().sum()/len(self.df_30)*100

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
        df_5_temp['Percent NaN'] = self.df_5.isnull().sum()/len(self.df_5)*100

        # combine the two stat DFs
        self.df_stats = pd.concat([df_5_temp, df_30_temp])

        # Print the DF
        if print_op == True:
            print(self.df_stats)

    def check_dates(self, first='2019-02-01', last='2019-02-20', print_op=True):
        '''This function takes a start date and an end date and attempts to use
        the web_api module to download each day of data and sotres the results
        in a pandas DF, with dates and regions with data showing 'Yes' and those
        without showing NaN.'''

        # generates a list of dates and regions to test
        date_range = pd.date_range(first, last).to_list()
        regions = ['sa1', 'nsw1', 'vic1', 'tas1', 'qld1']

        # creates the DF to store results
        date_df = pd.DataFrame(index=date_range, columns=regions)

        # iterate through regions and test each date in the list
        for reg in regions:

            for i in range(len(date_range)):
                if i+1 < len(date_range):

                    if print_op == True:
                        print('checking:', reg, date_range[i])

                    curr_date = str(date_range[i]).split(' ')[0]
                    next_date = str(date_range[i+1]).split(' ')[0]

                    try:
                        self.collect_data(d_start=(curr_date), d_end=(next_date), region=reg)
                        date_df.at[date_range[i], reg] = 'Yes'
                    except:
                        date_df.at[date_range[i], reg] = np.nan

        # Remove the last row whcih is empty and store as class variable
        self.date_df = date_df[:-1]

        # Print option
        if print_op == True:
            print(self.date_df[self.date_df.isna().any(axis=1)])

    def replace_null(self, field='all', method='weekly_avg'):
        '''Replaces any NaN or missing values using one of the methods out of
        median, interpolate, daily_avg or weekly_avg'''

        # Check that the method given is correct
        methods = [ 'zeros', 'median', 'interpolate', 'daily_avg', 'weekly_avg', 'delete']
        if method not in methods:
            raise DataHandlerError('Method must be one of: median, interpolate, \
                                    daily_avg, weekly_avg, zeros or delete')

        # Get a list of all fields
        if field == 'all':
            field = list(self.df_5) + list(self.df_30)

        # Converts y variable to a list if not a list
        if type(field) is not list:
            field = [field]

        if method == 'delete':
            self.rp_delete(field)

        if method == 'zeros':
            self.rp_zeros(field)

        if method == 'median':
            self.rp_median(field)

        if method == 'daily_avg':
            self.rp_daily_avg(field)

        if method == 'weekly_avg':
            self.rp_weekly_avg(field)

        if method == 'interpolate':
            self.rp_interpolate(field)

    def rp_delete(self, field):
        '''For each field given, removes any rows with a nan.'''

        for f in field:
            if f in list(self.df_5):
                self.df_5 = self.df_5[self.df_5[f].notna()]
            elif f in list(self.df_30):
                self.df_30 = self.df_30[self.df_30[f].notna()]

    def rp_zeros(self, field):
        '''For each field given, replaces any nan values with 0'''

        for f in field:
            # Replace all nan values with 0s
            if f in list(self.df_5):
                self.df_5[f].fillna(0, inplace=True)
            elif f in list(self.df_30):
                self.df_30[f].fillna(0, inplace=True)

    def rp_median(self, field):
        '''For each field given, replaces any nan values with the median value
        of that field'''

        for f in field:
            # replace all nan values with the median for that field
            if f in list(self.df_5):
                self.df_5[f].fillna(value=self.df_5[f].median(), inplace=True)
            if f in list(self.df_30):
                self.df_30[f].fillna(value=self.df_30[f].median(), inplace=True)

    def rp_daily_avg(self, field):
        '''For each field given, replaces any nan values with the mean average
        value for time of the day'''

        # Get the mean of each field for each day, hour and minute in the data
        # This is returned in a multiIndex dataframe
        df_5_mean = self.df_5.groupby([self.df_5.index.hour,
                        self.df_5.index.minute]).mean()
        df_30_mean = self.df_30.groupby([self.df_30.index.hour,
                        self.df_30.index.minute]).mean()

        # convert the multiindex index to a single index
        df_30_mean.index = ['{}_{}'.format(i, j) for i, j in df_30_mean.index]
        df_5_mean.index = ['{}_{}'.format(i, j) for i, j in df_5_mean.index]

        # Init the dicts that will contain the field and indexes of null values
        df_30_null_dict = {}
        df_5_null_dict = {}

        for f in field:
            # Populate the null_dicts
            if f in list(self.df_30):
                df_30_null_dict[f] = self.df_30[self.df_30[f].isnull()].index.tolist()
            if f in list(self.df_5):
                df_5_null_dict[f] = self.df_5[self.df_5[f].isnull()].index.tolist()

        # Iterate through each field and index in the dict and replace the
        # nan with the mean
        for k, v in df_30_null_dict.items():
            for i in v:
                hour = str(i).replace(' ', ':').split(':')[1]
                minute = str(i).replace(' ', ':').split(':')[2]
                mean_index = str(int(hour)) + '_' + str(int(minute))
                self.df_30.at[i, k] = df_30_mean[k][mean_index]

        # Iterate through each field and index in the dict and replace the
        # nan with the mean
        for k, v in df_5_null_dict.items():
            for i in v:
                hour = str(i).replace(' ', ':').split(':')[1]
                minute = str(i).replace(' ', ':').split(':')[2]
                mean_index = str(int(hour)) + '_' + str(int(minute))
                self.df_5.at[i, k] = df_5_mean[k][mean_index]

    def rp_weekly_avg(self, field):
        '''For each field given, replaces any nan values with the mean average
        value for time of the week'''

        # Get the mean of each field for each day, hour and minute in the data
        # This is returned in a multiIndex dataframe
        df_5_mean = self.df_5.groupby([self.df_5.index.weekday,
                        self.df_5.index.hour, self.df_5.index.minute]).mean()
        df_30_mean = self.df_30.groupby([self.df_30.index.weekday,
                        self.df_30.index.hour, self.df_30.index.minute]).mean()

        # convert the multiindex index to a single index
        df_30_mean.index = ['{}_{}_{}'.format(i, j, k) for i, j, k in df_30_mean.index]
        df_5_mean.index = ['{}_{}_{}'.format(i, j, k) for i, j, k in df_5_mean.index]

        # Init the dicts that will contain the field and indexes of null values
        df_30_null_dict = {}
        df_5_null_dict = {}

        for f in field:
            # Populate the null_dicts
            if f in list(self.df_30):
                df_30_null_dict[f] = self.df_30[self.df_30[f].isnull()].index.tolist()
            if f in list(self.df_5):
                df_5_null_dict[f] = self.df_5[self.df_5[f].isnull()].index.tolist()

        # Iterate through each field and index in the dict and replace the
        # nan with the mean
        for k, v in df_30_null_dict.items():
            for i in v:
                day = i.weekday()
                hour = str(i).replace(' ', ':').split(':')[1]
                minute = str(i).replace(' ', ':').split(':')[2]
                mean_index = str(day) + '_' + str(int(hour)) + '_' + str(int(minute))
                self.df_30.at[i, k] = df_30_mean[k][mean_index]

        # Iterate through each field and index in the dict and replace the
        # nan with the mean
        for k, v in df_5_null_dict.items():
            for i in v:
                day = i.weekday()
                hour = str(i).replace(' ', ':').split(':')[1]
                minute = str(i).replace(' ', ':').split(':')[2]
                mean_index = str(day) + '_' + str(int(hour)) + '_' + str(int(minute))
                self.df_5.at[i, k] = df_5_mean[k][mean_index]

    def rp_interpolate(self, field):
        '''for each field given, replace any NaN values with the interpolated
        values from the value before and after'''

        # Get the first and last indexes for each dataset
        df_30_ends = []
        df_5_ends = []
        df_30_ends.append(self.df_30.first_valid_index())
        df_30_ends.append(self.df_30.last_valid_index())
        df_5_ends.append(self.df_5.first_valid_index())
        df_5_ends.append(self.df_5.last_valid_index())

        # Init the dicts that will contain the field and indexes of null values
        df_30_null_dict = {}
        df_5_null_dict = {}

        for f in field:
            # Populate the null_dicts
            if f in list(self.df_30):
                df_30_null_dict[f] = self.df_30[self.df_30[f].isnull()].index.tolist()
            if f in list(self.df_5):
                df_5_null_dict[f] = self.df_5[self.df_5[f].isnull()].index.tolist()

        # Iterate through the null_dict key-value pairs and replace the
        # null values
        for k, v in df_30_null_dict.items():
            for i in v:
                if i not in df_30_ends:
                    self.interpolate_normal(k, i, 'df_30')
                else:
                    self.interpolate_ends(k, i, 'df_30', df_30_ends.index(i))

        # Iterate through the null_dict key-value pairs and replace the
        # null values
        for k, v in df_5_null_dict.items():
            for i in v:
                if i not in df_5_ends:
                    self.interpolate_normal(k, i, 'df_5')
                else:
                    self.interpolate_ends(k, i, 'df_5', df_5_ends.index(i))

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
