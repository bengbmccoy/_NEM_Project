'''
Written By Ben McCoy, May 2020

See the README for more detail about the general project.

This script contains a class object that can:
- Use the opennempy web_api module to collect NEM data from the OpenNem api
- Perform checks and verification of the data
- Organise and store the data in CSVs locally
- Open the data from local storage
'''

from opennempy import web_api
import datetime
import pandas as pd

def main():

    print('suh dude')


class DataHandler:
    def __init__(self):
        self.df_5 = None
        self.df_30 = None

    def print_data(self, res=5):
        '''Prints the data in short form for a given resolution'''
        if res == 5:
            print(self.df_5)
        if res == 30:
            print(self.df_30)

    def collect_from_web(self, d_start=(2018,1,1), d_end=(2019,12,12), region='sa1', print_op=False):
        '''This function takes a start dates as a tuple, a end date as a tupe, a
        region as a string and print_op as a boolean. The defaults are to take
        data from the 1/1/2018 to 12/12/2019 from SA. The function downloads 5 and
        30 minute data using the web_api from opennempy, between the d_start and
        d_end ranges from the region given. If the print_op variable is given as
        True, then the data is printed after being downloaded. If any errors occur,
        an exception is raised with DataHandlerError.'''


        if region not in ['nsw1', 'qld1', 'sa1','tas1','vic1']:
            raise DataHandlerError('Region must be one of nsw1, qld1, sa1, tas1, vic1')

        try:
            d1 = datetime.datetime(d_start[0], d_start[1], d_start[2])
            d2 = datetime.datetime(d_end[0], d_end[1], d_end[2])
        except:
            raise DataHandlerError('Issue with the input dates')

        print('Collecting data from OpenNEM web_api with properties:')
        print('Start date: \t' + str(d_start))
        print('End date: \t' + str(d_end))
        print('Region: \t' + convert_region_to_string(region))

        try:
            self.df_5, self.df_30 = web_api.load_data(d1=d1, d2=d2, region=region)
        except:
            raise DataHandlerError('Issue occurred during download')

        if print_op == True:
            print(self.df_5, self.df_30)

class DataHandlerError(Exception):
    pass


def convert_region_to_string(region):
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
