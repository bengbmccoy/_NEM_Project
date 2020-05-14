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
