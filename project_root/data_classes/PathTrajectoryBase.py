from abc import ABC, abstractmethod
import numpy as np
import utils.spatial_poses.se2_function as se2lib

class PathTrajectoryBase(ABC):
    """
    Base class for PathTrajectory implementations.
    """
    def __init__(self, df_path, path_xy):
        self.df_path = df_path
        self.df_path_xy = path_xy

    @abstractmethod
    def get_timestamps_ms(self):
        pass

    @abstractmethod
    def find_min_index(self, timestamps):
        pass

    @abstractmethod
    def find_path_and_car_pose(self, timestamp):
        pass

    def transform_to_world_coordinates(self, path_ego, car_pose):
        """
        Transforms the path from ego coordinates to world coordinates using SE2.
        Parameters:
        path (numpy array): The path in ego coordinates.
        car_pose (SE2): The car pose as an SE2 object.

        Returns:
        DataFrame: The path in world coordinates.
        """
        return se2lib.apply_se2_transform(car_pose, path_ego)

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

    def get_se2_from_vector(self, vector):
        """
        Converts a vector to an SE2 3x3 numpy array.

        Parameters:
        vector (numpy array): The vector to convert.

        Returns:
        SE2: 3x3 numpy array.
        """
        R = np.array([[np.cos(vector[2]), -np.sin(vector[2])], [np.sin(vector[2]), np.cos(vector[2])]])
        t = np.array([vector[0], vector[1]])
        SE2_mat = np.eye(3)
        SE2_mat[:2, :2] = R.squeeze()
        SE2_mat[:2, 2] = t.squeeze()
        return SE2_mat
    
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
    
    def get_path_xy(self):
        """
        Gets the path in ego coordinates.

        Returns:
        DataFrame: The path in ego coordinates.
        """
        return self.df_path_xy
    
    def get_df_path(self):
        """
        Gets the path in ego coordinates.

        Returns:
        DataFrame: The path in ego coordinates.
        """
        return self.df_path