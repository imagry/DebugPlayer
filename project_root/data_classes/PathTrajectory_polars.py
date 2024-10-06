# PathTrajectory_polars.py Class
import numpy as np
import polars as pl
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

    def __init__(self, df_path: pl.DataFrame, path_xy: pl.DataFrame):
        self.df_path = df_path
        self.df_path_xy = path_xy

        # Extract the time data of the path as a Polars Series
        self.time_data = df_path["data_timestamp_sec"]

    def find_min_index(self, timestamps: pl.Series) -> int:
        """
        Finds the index of the minimum value in the given timestamps Series.

        Parameters:
        timestamps (pl.Series): A Polars Series containing timestamp differences.

        Returns:
        int: The index of the minimum timestamp difference.
        """
        # Polars does not have an idxmin method, use arg_min instead
        min_index = timestamps.arg_min()
        return min_index

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

        # Convert car_pose_path to SE2 type                
        SE2_vector = np.array([w_car_pose_image_x, w_car_pose_image_y, w_car_pose_image_yaw_rad])
        SE2_mat = self.get_se2_from_vector(SE2_vector)
        car_pose_path_timestamp = SE2_mat
        
        # Extract the corresponding path from df_path_xy
        path_x_series = self.df_path_xy["path_x_data"][row_ind]
        path_y_series = self.df_path_xy["path_y_data"][row_ind]

        # Convert Polars Series to numpy arrays and remove NaN values
        path_x = path_x_series.drop_nulls().to_numpy().astype(float)
        path_y = path_y_series.drop_nulls().to_numpy().astype(float)

        # Combine path_x and path_y into a numpy array of shape (N, 2)
        path_xy = np.column_stack((path_x.T, path_y.T))

        if path_xy.size == 0 :
            raise ValueError(f"No path data found for timestamp {timestamp}")
        
        return path_xy, car_pose_path_timestamp

    def transform_to_world_coordinates(self, path_ego: np.ndarray, car_pose) -> np.ndarray:
        """
        Transforms the path from ego coordinates to world coordinates using SE2.

        Parameters:
        path_ego (numpy array): The path in ego coordinates.
        car_pose (SE2): The car pose as an SE2 object.

        Returns:
        numpy array: The path in world coordinates.
        """
        # Transform the path using the car_pose SE2 object
        path_world = se2lib.apply_se2_transform(car_pose, path_ego)

        return path_world

    def get_path_in_world_coordinates(self, timestamp: float) -> np.ndarray:
        """
        Gets the path in world coordinates for a given timestamp.

        Parameters:
        timestamp (float): The timestamp to get the path for.

        Returns:
        numpy array: The path in world coordinates.
        """
        path, car_pose = self.find_path_and_car_pose(timestamp)
        path_world = self.transform_to_world_coordinates(path, car_pose)
        return path_world

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