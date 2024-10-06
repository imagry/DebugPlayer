# PathTrajectory_polars.py Class
import numpy as np
import polars as pl
import utils.spatial_poses.se2_function as se2lib
from data_classes.PathTrajectoryBase import PathTrajectoryBase
from utils.data_loaders.path_handler_loader_polars import read_path_handler_data
class PathTrajectoryPolars(PathTrajectoryBase):
    """
    The class initializes with df_path which stores the paths of the trip in ego coordinates.
    For each path, it saves the timestamp of when the path was generated as well as the car pose at that time.
    It also provides the car pose at which time the path was processed to the file and the timestamp of that point.
    The class offers the following functionality:
    - For a given timestamp, it finds the path and the car pose at that time.
    - It then transforms the path from ego coordinates to world coordinates and returns the path in world coordinates.
    """

    def __init__(self, df_path, path_xy):
        df_path, path_xy = read_path_handler_data(df_path, path_xy)
        super().__init__(df_path, path_xy)
        self.time_data = df_path["data_timestamp_sec"]

    def get_timestamps(self):        
        return self.df_path["data_timestamp_sec"]
    
    def find_min_index(self, timestamps):
        return timestamps.arg_min()

    def find_path_and_car_pose(self, timestamp: float) -> tuple:
        """
        Finds the path and car pose at the given timestamp.

        Parameters:k
        timestamp (float): The timestamp to find the path and car pose.

        Returns:
        tuple: A tuple containing the path (as a numpy array) and the car pose (as an SE2 object).
        """
        # Calculate absolute differences between timestamps and the target timestamp
        time_diff = (self.time_data - timestamp).abs()

        # Find the index of the minimum difference
        row_ind = self.find_min_index(time_diff)

        # Retrieve the row at the found index
        row = self.df_path[row_ind]
    
        if row.is_empty():
            raise ValueError(f"No data found for timestamp {timestamp}")


        w_car_pose_image_x = row["w_car_pose_image_x"].str.strip_chars().cast(pl.Float64)[0]
        w_car_pose_image_y = row["w_car_pose_image_y"].str.strip_chars().cast(pl.Float64)[0]
        w_car_pose_image_yaw_rad = row["w_car_pose_image_yaw_rad"].str.strip_chars().cast(pl.Float64)[0]
        SE2_vector = np.array([w_car_pose_image_x, w_car_pose_image_y, w_car_pose_image_yaw_rad])
        car_pose_path = self.get_se2_from_vector(SE2_vector)
        
        # Extract the corresponding path from df_path_xy
        path_x_series = self.df_path_xy["path_x_data"][row_ind]
        path_y_series = self.df_path_xy["path_y_data"][row_ind]
        path_x = path_x_series.drop_nulls().to_numpy().astype(float)
        path_y = path_y_series.drop_nulls().to_numpy().astype(float)
        path_xy = np.column_stack((path_x.T, path_y.T))

        if path_xy.size == 0 :
            raise ValueError(f"No path data found for timestamp {timestamp}")
        
        return path_xy, car_pose_path


