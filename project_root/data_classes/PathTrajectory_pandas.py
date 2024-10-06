# PathTrajectory_pandas.py Class
import numpy as np
import pandas as pd
from data_classes.PathTrajectoryBase import PathTrajectoryBase
import utils.spatial_poses.se2_function as se2lib
from utils.data_loaders.path_handler_loader_pandas import read_path_handler_data
class PathTrajectoryPandas(PathTrajectoryBase):
    """
    The class initializes with df_path which stores the paths of the trip in ego coordinates.
    For each path, it saves the timestamp of when the path was generated as well as the car pose at that time.
    It also provides the car pose at which time the path was processed to the file and the timestamp of that point.
    The class offers the following functionality:
    - For a given timestamp, it finds the path and the car pose at that time.
    - It then transforms the path from ego coordinates to world coordinates and returns the path in world coordinates.
    """

    def __init__(self, file_path):
        df_path, path_xy = read_path_handler_data(file_path)
        super().__init__(df_path, path_xy)
        timestamp_s = pd.to_datetime(df_path['data_timestamp_sec'], unit='s')
        self.time_data_ms = timestamp_s.astype('int64') // 10**6
        
    
    def get_timestamps(self):
        return self.time_data_ms
            
    def find_min_index(self, timestamps):
        return timestamps.idxmin()         
    
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

        car_pose_path = self.df_path.loc[row_ind, ["car_pose_image_timestamp_sec", "w_car_pose_image_x", "w_car_pose_image_y", "w_car_pose_image_yaw_rad"]]
        SE2_vector = np.array([car_pose_path["w_car_pose_image_x"], car_pose_path["w_car_pose_image_y"], car_pose_path["w_car_pose_image_yaw_rad"]])
        car_pose_path = self.get_se2_from_vector(SE2_vector)
        
        # Extract the corresponding path from the path_xy
        path_x = self.df_path_xy['path_x_data'].iloc[row_ind]
        path_y = self.df_path_xy['path_y_data'].iloc[row_ind]
        path_x = pd.to_numeric(path_x.dropna())
        path_y = pd.to_numeric(path_y.dropna())
        path_xy = np.column_stack((path_x, path_y))        

        return path_xy, car_pose_path





    
    
