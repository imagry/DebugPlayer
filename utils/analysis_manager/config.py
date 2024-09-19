# config.py

import os

increment = 250  # Initial increment in milliseconds    


# define an enum to the different types of df_* dataframes
class DataFrameType:
    STEERING = 0
    CAR_POSE = 1        
    # Add more types here                

# define an enum to the different types of Data Class Objects
class ClassObjType:
    PATH = 0
    PATH_EXTRACTION = 1
    PATH_ADJUSTMENT = 2
    # Add more types here  
        
# Define car dimensions        # 
carmodel = 'Aria'



if carmodel == 'Aria':
    W, L, wb, b_f, b_r = 1.5, 4.5, 2.8, 1.2, 0.5
    arm = 0.0

def initialize_parameters():
    trip1 = '2024-09-06T16_23_19' # merger = 1  steering_fix = 0
    trip2 = '2024-09-06T16_31_35' # merger = 0  steering_fix = 0
    trip3 = '2024-09-06T16_49_58' # merger = 1  steering_fix = 1 
    trip4 = '2024-09-06T16_54_21' # merger = 1  steering_fix = 1
    trip5 = '2024-09-06T17_01_42' # merger = 0  steering_fix = 1
    trip_Man_1 = '2024-09-06T17_15_54' # Manual
    trip_Man_2 = '2024-09-06T17_19_36' # Manual
    trip6 = '2024-09-11T15_36_18'
    trip7 = '2024-09-11T15_55_30'
    trip8 = '2024-09-11T15_59_45'
    
    params = {
        'spline_ds': 0.1,  # spline interpolation step
        'spline_degree': 3,  # spline interpolation degree
        'plot_settings': {
            'print_trip_map': True,
            'plot_poses': False,
            'plot_ego': False,
            'plot_after_merge': False,
        },
        'trip_settings': {
            'Run_alternative_trip': True,
            'alternative_trip_name': trip8,
            'trip_path': os.environ.get('OFFLINE_DATA_PATH_URBAN'),
            'data_ds_factor': 1,
            'transform_from_CFA_to_COG': False,
        },
        'PathAssemblerOptions': {
            'path_start_ind': 0,
            'path_end_ind': 300,
            'delay': 0.35,
            'path_points_skip': 1,
            'path_length_to_eval': 100,
            'frames_skip': 0,
            'refractory_period_sec': 0.5
        },
    }
    return params