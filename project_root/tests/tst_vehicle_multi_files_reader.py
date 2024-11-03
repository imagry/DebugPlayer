import sys
import os
import matplotlib.pyplot as plt
from math import isclose

from utils.data_loaders.vehicle_states_multi_file_reader import read_vehicle_state_logs



def test_reading_vehicle_log_files(file_path):
    
    #  Reading the file with polars
    df_cruise_control, df_driving_mode, df_speed, df_steering = read_vehicle_state_logs(file_path)
    
    
        
if __name__ == "__main__":
    trip_path = "/home/thamam/data/trips/2024-09-19T13_25_15/"
    
    test_reading_vehicle_log_files(trip_path)
