import numpy as np
import pandas as pd
from utils.se2_function import *

def read_path_data_old(trip_path):
        
    # read data 
    filepath_nissan_proto_dump =  trip_path +'/'+ 'nissan_exported_data.csv'
    # gps_header = ['time_stamp','latitude','longtitude','height','speed','sensor_time_counter']

    points_num = 300 #number of points recorded per path sample
    df_path_ = pd.read_csv(filepath_nissan_proto_dump, header=0)
    timestamp_ind=0 # time stamp of frame
    # timestampsend_ind=1  # time stamp of when the frame was sent to protobuf
    target_speed_ind=1  
    turn_signal_state_ind=2
    # path_x_ind = turn_signal_state_ind+np.linspace(1,points_num)
    path_x_ind = np.arange(1, points_num+1) + turn_signal_state_ind
    path_y_ind = np.arange(1, points_num+1) + path_x_ind[-1]

    x = df_path_.iloc[:, path_x_ind]
    y = df_path_.iloc[:, path_y_ind]
    t = df_path_.iloc[:, timestamp_ind]
    if t[0]>1e11:
        t = t/1000 #convert from ms to seconds if needed
    v = df_path_.iloc[:, target_speed_ind]
            
    return x,y,t,v
   
def read_path_data(trip_path):
    
    # Breakdown trip_path into its components
    trip_path_split = trip_path.split('/')
    trip_name = trip_path_split[-1]
    # extract the date from the trip_name using the format '2024-07-22T14_05_07'
    trip_date = trip_name.split('T')[0]
        
    # if date of trip_name is before 02/08/2024 then switch to old reader
    if trip_name < '2024-08-02':
        return read_path_data_old(trip_path)
        
    # read data 
    filepath_nissan_proto_dump =  trip_path +'/'+ 'nissan_exported_data.csv'
    # gps_header = ['time_stamp','latitude','longtitude','height','speed','sensor_time_counter']

    points_num = 300 #number of points recorded per path sample
    df_path_ = pd.read_csv(filepath_nissan_proto_dump, header=0)
    timestamp_ind=0 # time stamp of frame
    timestampsend_ind=1  # time stamp of when the frame was sent to protobuf
    target_speed_ind=2  
    turn_signal_state_ind=3
    # path_x_ind = turn_signal_state_ind+np.linspace(1,points_num)
    path_x_ind = np.arange(1, points_num+1) + turn_signal_state_ind
    path_y_ind = np.arange(1, points_num+1) + path_x_ind[-1]

    x = df_path_.iloc[:, path_x_ind]
    y = df_path_.iloc[:, path_y_ind]
    t = df_path_.iloc[:, timestamp_ind]
    if t[0]>1e11:
        t = t/1000 #convert from ms to seconds if needed
    v = df_path_.iloc[:, target_speed_ind]
            
    return x,y,t,v

def read_nissan_imu_data(trip_path):
# read IMU Yaw data 
    filepath_imu =  trip_path +'/'+ 'imu.csv'
    # gps_header = ['time_stamp','latitude','longtitude','height','speed','sensor_time_counter']

    # Set the data types of your columns
    dtypes = {
        'time_stamp': 'float64',
        'yaw': 'float64',
        'sensor_time_counter': 'int64',        
        # Add more columns as needed
    }

    df_imu_ = pd.read_csv(filepath_imu, header=0, dtype=dtypes)
    
    df_imu =  df_imu_[['time_stamp','yaw','sensor_time_counter']]

    return df_imu
# Sample data: replace these with your actual latitude and longitude points
