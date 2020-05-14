'''
Written By Ben McCoy, May 2020

This script will run tests on the data_handler.py code to ensure it is working
as expected using the unittest module.

To run the tests, simply use the command:
    python -m unittest_data_handler
'''

import unittest
import pandas as pd
import datetime
import numpy as np

from data_handler import DataHandler

class TestDataHandler(unittest.TestCase):
    def setUp(self):
        '''This functions sets up two dataframes with a simeple data set to be
        used for testing.'''

        start = datetime.datetime(2019,1,1)
        columns_5 = ['A', 'B', 'C']
        columns_30 = ['D', 'E', 'F']
        dt_list_5 = datetime_list(start, 5, 60)
        dt_list_30 = datetime_list(start, 30, 10)

        self.df_5 = pd.DataFrame(index=dt_list_5, columns=columns_5)
        self.df_30 = pd.DataFrame(index=dt_list_30, columns=columns_30)

        for i in columns_5:
            self.df_5[i] = list(range(len(self.df_5)))

        for i in columns_30:
            self.df_30[i] = list(range(len(self.df_30)))

    def test_replace_null_interpolate(self):
        '''This function adds np.nan values to copies of self.df_5 and self.df_30
        and then sets the values of df_5 and df_30 in test_handler to the new
        copies of df_5 and df_30. Then the replace_null(method='interpolate')
        function is called on test_handler whcih should replace the np.nan values
        with interpolated values. Finally assertEqual is called to check that the
        replace_null function is working correctly.'''

        df_5_replace_null_check = self.df_5.copy()
        df_5_replace_null_check.loc[self.df_5.first_valid_index(), 'C'] = np.nan

        df_30_replace_null_check = self.df_30.copy()
        df_30_replace_null_check.loc[self.df_30.last_valid_index(), 'D'] = np.nan

        test_handler = DataHandler()
        test_handler.df_5 = df_5_replace_null_check
        test_handler.df_30 = df_30_replace_null_check
        test_handler.replace_null(method='interpolate')

        self.assertEqual(test_handler.df_5.loc[test_handler.df_5.first_valid_index(), 'C'], 1.0)
        self.assertEqual(test_handler.df_30.loc[test_handler.df_30.last_valid_index(), 'D'], 8.0)

    def test_replace_null_median(self):
        '''This function adds np.nan values to copies of self.df_5 and self.df_30
        and then sets the values of df_5 and df_30 in test_handler to the new
        copies of df_5 and df_30. Then the replace_null(method='median')
        function is called on test_handler whcih should replace the np.nan values
        with median values. Finally assertEqual is called to check that the
        replace_null function is working correctly.'''

        df_5_replace_null_check = self.df_5.copy()
        df_5_replace_null_check.loc[self.df_5.first_valid_index(), 'C'] = np.nan

        df_30_replace_null_check = self.df_30.copy()
        df_30_replace_null_check.loc[self.df_30.last_valid_index(), 'D'] = np.nan

        test_handler = DataHandler()
        test_handler.df_5 = df_5_replace_null_check
        test_handler.df_30 = df_30_replace_null_check
        test_handler.replace_null(method='median')

        self.assertEqual(test_handler.df_5.loc[test_handler.df_5.first_valid_index(), 'C'], 30.0)
        self.assertEqual(test_handler.df_30.loc[test_handler.df_30.last_valid_index(), 'D'], 4.0)

    def test_data_stats(self):
        '''This function sets the values of test_handler.df_5 and test_handler.df_30
        to the values self.df_5 and self.df_30 and then calls the data_stats function
        on the test_handler. Finally assertEqual is called to see if the correct
        values are calculated.'''

        test_handler = DataHandler()
        test_handler.df_5 = self.df_5
        test_handler.df_30 = self.df_30
        test_handler.data_stats(print_op=False)

        self.assertEqual(test_handler.df_stats['Mean']['A'], 29.5)
        self.assertEqual(test_handler.df_stats['Median']['C'], 29.5)
        self.assertEqual(test_handler.df_stats['Min']['D'], 0)
        self.assertEqual(test_handler.df_stats['Max']['E'], 9)
        self.assertEqual(test_handler.df_stats['Count']['F'], 10)

def datetime_list(start, timediff, length):
    temp_list = []
    for i in range(length):
        temp_list.append(start + datetime.timedelta(minutes=(timediff*(i+1))))
    return temp_list
