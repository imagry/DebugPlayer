# data_loader.py
import numpy as np
import pandas as pd
import os
import sys

# current_dir = os.path.dirname(os.path.abspath(__file__))
# parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
# sys.path.insert(0, f"{parent_dir}/utils")


def load_trip_cruise_control_data(trip_path):
    cc_file = trip_path + r"/cruise_control.csv"
    df_cc = pd.read_csv(cc_file)
    return df_cc

def load_trip_car_pose_data(car_pose_file):    
    df_car_pose = pd.read_csv(car_pose_file)
    return df_car_pose
    
def load_trip_steering_data(steering_file_path):    
    df_steering = pd.read_csv(steering_file_path)
    # change the column name of the steering data from data_value to "current_steering_deg"
    df_steering.rename(columns={'data_value': 'current_steering_deg'}, inplace=True)
    # change the column name of "time_stamp" to "timestamp"
    df_steering.rename(columns={'time_stamp': 'timestamp'}, inplace=True)
    
    return df_steering


