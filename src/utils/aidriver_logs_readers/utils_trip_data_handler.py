import json
import numpy as np
import pandas as pd
import utils.utils_geo as geo
import os
import yaml
import socket
import yaml


def load_trips(config_path):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def get_trip_string(config_path, trip_name):
    trips = load_trips(config_path)
    return trips.get(trip_name, "Trip name not found")


# Example usage
# config_path = 'path/to/trips.yaml'
# trip_name = 'trip_1'
# trip_string = get_trip_string(config_path, trip_name)
# print(trip_string)

def load_multiple_trips(trips_dir, trips, coordinates_type, data_ds_factor=1):
    
    if coordinates_type=="wgs_84":
        Xgps_long_lat = np.empty((3,0))
    elif coordinates_type == "rect":
        Xrect   = np.empty((3,0))
    else:
        Xgps_long_lat = pd.array()
        Xrect   = np.empty((3,0))
        
    for trip in trips:
        trip_path = trips_dir + trip
        if coordinates_type=="wgs_84":            
            Xgps_long_lat_ = load_trip_gps_data(trip_path,coordinates_type="wgs_84", sample_spacing = data_ds_factor)
            Xgps_long_lat = np.concatenate((Xgps_long_lat,Xgps_long_lat_),axis=1)
        elif coordinates_type=="rect":
            Xrect_ = load_trip_gps_data(trip_path,coordinates_type="rect", sample_spacing = data_ds_factor)
            Xrect = np.concatenate((Xrect, Xrect_), axis = 1)
        else:
            Xgps_long_lat, Xrect = load_trip_gps_data(trip_path,coordinates_type="both", sample_spacing = data_ds_factor)
            Xgps_long_lat = np.concatenate((Xgps_long_lat,Xgps_long_lat_),axis=1)
            Xrect = np.concatenate((Xrect, Xrect_), axis = 1)

    if coordinates_type=="wgs_84":
        return Xgps_long_lat
    elif coordinates_type == "rect":
        return Xrect 
    else:
        return Xgps_long_lat, Xrect
    
def load_carPoseManager_data(trip_path, cpm_fileName, data_ds_factor):
    
    cpm_path = trip_path +'/'+ cpm_fileName 

    # read car pose manager file
    cpm_header = ['system_time_stamp', 'sensor_time_stamp','x','y','yaw']
    
    df_cpm = pd.read_csv(cpm_path, names=cpm_header, skiprows=2, header=0, index_col=False)

    timestamp_ai   = np.squeeze(df_cpm[['system_time_stamp']].iloc[::data_ds_factor,:])   
    timestamp_imu = np.squeeze(df_cpm[['sensor_time_stamp']].iloc[::data_ds_factor,:])   
    x   = np.squeeze(df_cpm[['x']].iloc[::data_ds_factor,:])   
    y   = np.squeeze(df_cpm[['y']].iloc[::data_ds_factor,:])   
    yaw = np.squeeze(df_cpm[['yaw']].iloc[::data_ds_factor,:])   


    X = np.asarray([x,y])
    Xh = np.append(X,np.ones((1,x.size)),axis=0)
    
    return Xh

def load_trip_gps_data(trip_path, coordinates_type, sample_spacing = 1, tangent_frame = "ENU"):
    # read position from gps data 
    filepathGPS =  trip_path +'/'+ 'gps.csv'
    # gps_header = ['time_stamp','latitude','longtitude','height','speed','sensor_time_counter']
    
    # Set the data types of your columns
    dtypes = {
        'latitude': 'float64',
        'longitude': 'float64',
        'height': 'float64',
        'time_stamp': 'float64'
        # Add more columns as needed
    }
    
    df_gps = pd.read_csv(filepathGPS, header=0, dtype=dtypes)
    df_wgs84 = df_gps[['latitude','longitude','height']].iloc[::sample_spacing,:]
    Xwgs84_long_lat = np.asarray(df_wgs84[['longitude','latitude','height']]).T
    time_vec_ = np.squeeze(np.asarray(df_gps[['time_stamp']].iloc[::sample_spacing,:]).T)
    # Xwgs84_h = np.append(Xwgs84,np.ones((1,Xwgs84.shape[1])),axis = 0)
    
    # adding the time_stamp column to the result
    Xwgs84_long_lat_ = np.hstack((Xwgs84_long_lat.T, time_vec_.reshape(-1, 1)))
    Xwgs84_long_lat = Xwgs84_long_lat_.T
  
    if coordinates_type=="wgs_84":
        return Xwgs84_long_lat
    
    # Then: coordinates_type=="both" or coordinates_type=="rect":
    # convert gps path from wgs84 to rectangular coordinates
    # a,e,f,RN_at_lat = geo.get_wgs84_geodetic_model()

    # print( abs(RN_at_lat(np.radians(34))  - RN_at_lat(np.radians(32)))/RN_at_lat(np.radians(32)))
    # geoModelParams = {'a':a,'e':e,'f':f,'RN_h':RN_at_lat}
    
    df_ecef = geo.wgs842ecef(df_wgs84[['longitude','latitude','height']])
    
    # set first coordinate as ENU reference point
    XYZ_ref = df_ecef.iloc[0,:]
    if tangent_frame=="ENU":
        df_tangent = geo.ecef2enu(df_ecef,XYZ_ref, df_wgs84['latitude'].iloc[0], df_wgs84['longitude'].iloc[0])
    elif tangent_frame=="NED":
        df_tangent = geo.ecef2ned(df_ecef,XYZ_ref, df_wgs84['latitude'].iloc[0], df_wgs84['longitude'].iloc[0])
    else:
        SystemError("Bad tangent_frame name \n")
        
    # xyz_enu = np.asarray(df_enu).T
    # # change into homogeneous coordinates     
    # X_rect_h = np.append(X_rect,np.ones((1,X_rect.shape[1])),axis = 0)
    
    # Adding time_stamp column
    df_tangent['time_stamp'] = time_vec_

    if coordinates_type=="rect":
        return df_tangent
    else: # coordinates_type == 'both'
        return Xwgs84_long_lat, df_tangent

def load_trip_data(trip_dir):
    gps_file = trip_dir + r"/gps.csv"
    imu_file = trip_dir + r"/imu.csv"
    speed_file = trip_dir + r"/speed.csv"
    steering_file = trip_dir + r"/steering.csv"
    car_info_file = trip_dir + r"/car_info.json"

    df_gps = None
    try:
        df_gps = pd.read_csv(gps_file)
    except (FileNotFoundError, pd.errors.EmptyDataError):
        pass

    df_imu = None
    try:
        df_imu = pd.read_csv(imu_file)
    except FileNotFoundError:
        pass

    df_speed = pd.read_csv(speed_file)
    df_speed.rename(columns={'data_value': 'speed'}, inplace=True)
    df_steering = pd.read_csv(steering_file)
    df_steering.rename(columns={'data_value': 'steering'}, inplace=True)

    with open(car_info_file) as f:
        json_car = json.load(f)
        
    return df_gps, df_imu, df_speed, df_steering, json_car

def consolidate_dfs(*dataframes):
    result = dataframes[0].copy()
    for df in dataframes[1:]:
        ts_column = df['time_stamp']
        
        for name, values in df.items():
            # First column is the time_stamp
            if name == 'time_stamp':
                continue
                
            # Interpolate values to the timestamps of the leading dataframe
            interpolated_values = np.interp(result['time_stamp'], ts_column, values)
            result[name] = interpolated_values
            
    return result




