from scipy.interpolate import interp1d
import pandas as pd
from utils.data_loaders.li_fsm_data_loader import read_li_fsm_logs


class LiFsmInfo:
    ''' This class is used to load the large intersection FSM data. 
    '''
    def __init__(self, trip_path): 
        self.trip_path = trip_path
             
        
    def get_timestamps_seconds(self):
        ''' Get the timestamps in seconds.
        
            Returns:
            pandas.Series: The timestamps in seconds.
        '''
        return self.timestamps.astype('int64') // 10**9
    
    def get_timestamps_milliseconds(self):
        ''' Get the timestamps in milliseconds.
        
            Returns:
            pandas.Series: The timestamps in milliseconds.
        '''
        return self.timestamps.astype('int64') // 10**6
    
    def get_timestamps_datetime(self):
        ''' Get the timestamps as datetime.
        
            Returns:
            pandas.Series: The timestamps as datetime.
        '''
        return pd.to_datetime(self.timestamps, unit='ms')            
    
    def get_timestamps(self):
        ''' Get the timestamps.
        
            Returns:
            pandas.Series: The timestamps.
        '''
        return self.timestamps