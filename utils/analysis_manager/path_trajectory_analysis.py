# path_trajectory_analysis.py

from analysis_manager import localization_utils as lu

# # data_handling.py
def path_trajectroy_analysis(df_path, interpolation=False):
    """Merge the time series data of steering and car pose."""
    
    return 

import pandas as pd
import numpy as np

class PathTrajectory:
    """
    The class initializes with df_path which stores the paths of the trip in ego coordinates.
    For each path, it saves the timestamp of when the path was generated as well as the car pose at that time.
    It also provides the car pose at which time the path was processed to the file and the timestamp of that point.
    The class offers the following functionality:
    - For a given timestamp, it finds the path and the car pose at that time.
    - It then transforms the path from ego coordinates to world coordinates and returns the path in world coordinates.
    """

    def __init__(self, df_path):
        self.df_path = df_path

    def find_path_and_car_pose(self, timestamp):
        """
        Finds the path and car pose at the given timestamp.

        Parameters:
        timestamp (float): The timestamp to find the path and car pose.

        Returns:
        tuple: A tuple containing the path (as a DataFrame) and the car pose (as a Series).
        """
        # Find the row corresponding to the given timestamp
        row = self.df_path[self.df_path['data_timestamp_sec'] == timestamp]
        if row.empty:
            raise ValueError(f"No data found for timestamp {timestamp}")

        # Extract the car pose
        car_pose = row[['w_car_pose_now_x_', 'w_car_pose_now_y', 'w_car_pose_now_yaw_rad']].iloc[0]

        # Extract the path columns
        path_columns = [col for col in self.df_path.columns if col.startswith('path_x_') or col.startswith('path_y_')]
        path = row[path_columns]

        return path, car_pose

    def transform_to_world_coordinates(self, path, car_pose):
        """
        Transforms the path from ego coordinates to world coordinates.

        Parameters:
        path (DataFrame): The path in ego coordinates.
        car_pose (Series): The car pose containing x, y, and yaw.

        Returns:
        DataFrame: The path in world coordinates.
        """
        # Extract car pose components
        car_x = car_pose['w_car_pose_now_x_']
        car_y = car_pose['w_car_pose_now_y']
        car_yaw = car_pose['w_car_pose_now_yaw_rad']

        # Initialize lists to store transformed coordinates
        world_x = []
        world_y = []

        # Iterate over path columns
        for i in range(len(path.columns) // 2):
            ego_x = path[f'path_x_{i}'].values[0]
            ego_y = path[f'path_y_{i}'].values[0]

            # Transform coordinates
            world_x_i = car_x + ego_x * np.cos(car_yaw) - ego_y * np.sin(car_yaw)
            world_y_i = car_y + ego_x * np.sin(car_yaw) + ego_y * np.cos(car_yaw)

            world_x.append(world_x_i)
            world_y.append(world_y_i)

        # Create DataFrame for world coordinates
        world_coordinates = pd.DataFrame({
            f'world_x_{i}': world_x,
            f'world_y_{i}': world_y
        })

        return world_coordinates

    def get_path_in_world_coordinates(self, timestamp):
        """
        Gets the path in world coordinates for a given timestamp.

        Parameters:
        timestamp (float): The timestamp to get the path for.

        Returns:
        DataFrame: The path in world coordinates.
        """
        path, car_pose = self.find_path_and_car_pose(timestamp)
        world_path = self.transform_to_world_coordinates(path, car_pose)
        return world_path

# Example usage
# df_path = pd.read_csv('path_to_your_csv_file.csv')
# path_trajectory = PathTrajectory(df_path)
# timestamp = 1234567890.0
# world_path = path_trajectory.get_path_in_world_coordinates(timestamp)
# print(world_path)