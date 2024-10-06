# PathTrajectory_pandas.py Class

import numpy as np
import pandas as pd

import utils.spatial_poses.se2_function as se2lib
class PathTrajectory:
    """
    The class initializes with df_path which stores the paths of the trip in ego coordinates.
    For each path, it saves the timestamp of when the path was generated as well as the car pose at that time.
    It also provides the car pose at which time the path was processed to the file and the timestamp of that point.
    The class offers the following functionality:
    - For a given timestamp, it finds the path and the car pose at that time.
    - It then transforms the path from ego coordinates to world coordinates and returns the path in world coordinates.
    """

    def __init__(self, df_path, path_xy):
        self.df_path = df_path
        self.df_path_xy = path_xy
        
        # Extract the time data of the path        
        timestamp_s = pd.to_datetime(df_path['data_timestamp_sec'], unit='s')        
        self.time_data_ms = timestamp_s.astype('int64') // 10**6 
    
    def get_timestamps(self):
        return self.time_data_ms   
    
    def find_min_index(self, timestamps):
        
        if isinstance(self.time_data_ms, (pd.Series, pd.DataFrame)):
            # If self.time_data is a pandas Series or DataFrame
            min_index = timestamps.idxmin()
        else:
            raise TypeError("Unsupported data type for self.time_data")
        
        return min_index             
    
    
    def find_path_and_car_pose(self, timestamp_ms):
        """
        Finds the path and car pose at the given timestamp.

        Parameters:
        timestamp (float): The timestamp to find the path and car pose.

        Returns:
        tuple: A tuple containing the path (as a DataFrame) and the car pose (as an SE2 object).
        """
        # Find the row index of the entry closest to the given timestamp
        row_ind = self.find_min_index(np.abs(self.time_data_ms - timestamp_ms))
        row = self.df_path.loc[row_ind]
        
        if row.empty:
            raise ValueError(f"No data found for timestamp {timestamp_ms}")

        # Extract the car pose
        car_pose_path = self.df_path.loc[row_ind, ["car_pose_now_timestamp", "w_car_pose_image_x", "w_car_pose_image_y", "w_car_pose_image_yaw_rad"]]

        # Convert car_pose_path to SE2 type
        SE2_vector = np.array([car_pose_path["w_car_pose_image_x"], car_pose_path["w_car_pose_image_y"], car_pose_path["w_car_pose_image_yaw_rad"]])
        SE2_mat = self.get_se2_from_vector(SE2_vector)
        car_pose_path = SE2_mat
        
        # Extract the corresponding path from the path_xy
        path_x = self.df_path_xy['path_x_data'].iloc[row_ind]
        path_y = self.df_path_xy['path_y_data'].iloc[row_ind]
        
        # Remove NaN values
        path_x = pd.to_numeric(path_x.dropna())
        path_y = pd.to_numeric(path_y.dropna())
        
        # Combine path_x and path_y into numpy array of shape (N, 2)
        path_xy = np.column_stack((path_x, path_y))        

        return path_xy, car_pose_path

    def transform_to_world_coordinates(self, path_ego, car_pose):
        """
        Transforms the path from ego coordinates to world coordinates using SE2.

        Parameters:
        path (numpy array): The path in ego coordinates.
        car_pose (SE2): The car pose as an SE2 object.

        Returns:
        DataFrame: The path in world coordinates.
        """
        # Transform the path using the car_pose SE2 object
        path_world = se2lib.apply_se2_transform(car_pose, path_ego)

        return path_world

    def get_path_in_world_coordinates(self, timestamp):
        """
        Gets the path in world coordinates for a given timestamp.

        Parameters:
        timestamp (float): The timestamp to get the path for.

        Returns:
        DataFrame: The path in world coordinates.
        """
        path, car_pose = self.find_path_and_car_pose(timestamp)
        path_world = self.transform_to_world_coordinates(path, car_pose)
        return path_world, car_pose
    
    
    def get_current_speed(self, timestamp):
        """
        Gets the current speed for a given timestamp.

        Parameters:
        timestamp (float): The timestamp to get the speed for.

        Returns:
        float: The current speed.
        """      
        # Find the row index of the entry closest to the given timestamp
        row_ind = self.find_min_index(np.abs(self.time_data_ms - timestamp))
        row = self.df_path.loc[row_ind]
        
        if row.empty:
            raise ValueError(f"No data found for timestamp {timestamp}")

        # Extract the speed
        speed = self.df_path.loc[row_ind, "current_speed_mps"]

        return speed
    
    def get_se2_from_vector(self, vector):
        """
        Converts a vector to an SE2 3x3 numpyarray 

        Parameters:
        vector (numpy array): of the form (t_x, t_y, theta)  - The vector to convert.

        Returns:
        SE2: 3x3 numpy array where SE2 = [ R(theta) , t; 0 0 1] with R aA 2X2 rotation matrix and t =[t_x;t_y] is  2x1 vector of the translation
        """
        R = np.array([[np.cos(vector[2]), -np.sin(vector[2])], [np.sin(vector[2]), np.cos(vector[2])]])
        t = np.array([vector[0], vector[1]])
        SE2_mat = np.eye(3)
        SE2_mat[:2,:2] = R
        SE2_mat[:2,2] = t
        return SE2_mat
