# PathRegressor.py
import os
import sys
import pickle
import pandas as pd
import numpy as np
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, as_completed
import data_preparation as dp 
from analysis_manager.DataClasses.PathTrajectory_pandas import PathTrajectory
from typing import TypeAlias

# Custom type alias for DataFrame with specific columns
PathDataFrame: TypeAlias = pd.DataFrame


class PathRegressor:
    """ The class is used to generate a regression model for the path data. 
    It takes as an input a PathTrajectory object and uses it to extract from each generated path a key points which 
    are used to generate a full trajectory. The idea is to be able to run the model whenever there is a new SW version 
    on trip and compare the path planner output and observe if there are any key differences in ther behaviour of the 
    across the two paths. 
    The class offers the following functionality:
    - Extract key points from the path data
    - Generate a an equivalent trajectory from the the extracted points. 
    - Evaluate KPI of the generated trajectory.    
    """
    def __init__(self, pathobj:PathTrajectory , carpose, CACHE_DIR = "cache", delta_t_sec=0.1, pts_before=0, pts_after=0, max_workers= 1):
        self.pathobj = pathobj
        self.df_path = pathobj.df_path
        self.df_path_xy = pathobj.df_path_xy
        self.time_data = pathobj.time_data
        self.carpose = carpose
        self.CACHE_DIR = CACHE_DIR
        self.pts_before = pts_before  # New attribute to store the number of points
        self.pts_after = pts_after  # New attribute to store the number of points
        self.delta_t_sec = delta_t_sec
        self.max_workers = max_workers
        
        self.df_path_xy = self.df_path_xy
        self.df_key_points = None   # New attribute to store the key points
        self.df_trajectory = None   # New attribute to store the trajectory
        self.kpi = None            # New attribute to store the KPI
        
    def update_params(self, params_dict):
        """ Update the parameters of the path regressor. """
        self.pts_before = params_dict['pts_before'] if 'pts_before' in params_dict else self.pts_before
        self.pts_after = params_dict['pts_after'] if 'pts_after' in params_dict else self.pts_after
        self.delta_t_sec = params_dict['delta_t_sec'] if 'delta_t_sec' in params_dict else self.delta_t_sec
        self.max_workers = params_dict['max_workers'] if 'max_workers' in params_dict else self.max_workers
        
        return
    
            
    def extract_key_points(self):
        """ Extract key points from the path data. The key points are used to generate a full trajectory. 
        The idea is to be able to run the model whenever there is a new SW version on trip and compare the path planner 
        output and observe if there are any key differences in ther behaviour of the across the two paths. 
        """
        # Extract key points from the path data
        self.df_key_points = self.df_path_xy.iloc[::10]
        self.df_key_points = self.df_key_points.reset_index(drop=True)
        
        return self.df_key_points
    
    def generate_trajectory(self, df_key_points):
        """ Generate a an equivalent trajectory from the the extracted points. """
        # Generate a an equivalent trajectory from the the extracted points
        self.df_trajectory = self.pathobj.generate_trajectory(df_key_points)
        
        return self.df_trajectory   
    
    def evaluate_kpi(self, df_trajectory):
        """ Evaluate KPI of the generated trajectory. """
        # Evaluate KPI of the generated trajectory
        self.kpi = self.pathobj.evaluate_kpi(df_trajectory)
        
        return self.kpi
    
    def extract_path_points_at_timestamp(self, path, timestamp: float, speed: float):      
        """
        Extract path points at a specific timestamp.

        Args:
            path (pd.DataFrame): A DataFrame with columns 'timestamp', 'path_x_data', 'path_y_data'.
            timestamp (float): The timestamp at which to extract the path points.
            speed (float): The speed at the timestamp.

        Returns:
            pd.DataFrame: A DataFrame with the extracted path points.

        Algorithm Description:
            Based on delta_t_sec*v you find the midpoint that is closest to that arc_length distance, and then create a vector of path points from the indexes [mid_point_index - pts_before, mid_point_index, mid_point_index+pts_after].
        """
        if path.shape[0] == 2:
            x_data = path[0].T
            y_data = path[1].T
        elif path.shape[1] == 2:
            x_data = path[:,0]
            y_data = path[:,1]
        else:
            raise ValueError("Invalid path dimensions")
                            
        # Compute cumulative distances along the path
        distances = np.sqrt(np.diff(x_data)**2 + np.diff(y_data)**2)
        cumulative_distances = np.insert(np.cumsum(distances), 0, 0)

        # Compute delta_s
        delta_s = self.delta_t_sec * speed

        # Find the index where cumulative distance is closest to delta_s
        mid_point_index = np.argmin(np.abs(cumulative_distances - delta_s))

        # Collect points from mid_point_index - pts_before to mid_point_index + pts_after
        start_index = max(mid_point_index - self.pts_before, 0)
        end_index = min(mid_point_index + self.pts_after + 1, len(x_data))

        extracted_x = x_data[start_index:end_index]
        extracted_y = y_data[start_index:end_index]

        # Return as DataFrame
        extracted_points = pd.DataFrame({'x': extracted_x, 'y': extracted_y})

        return extracted_points
    
    def extract_virtual_path_parallel(self):
        """
        Extract path points at each timestamp in parallel.                          
                
        Returns:
            pd.DataFrame: A DataFrame with the extracted path points.
            np.array: An array with the extracted path points and other metrics.
            
        Algorithm Description:
            For each timestamp, extract path points, compute speed and other metrics.
            Use ThreadPoolExecutor to parallelize the processing of each timestamp.
        """
        def process_timestamp(idx, timestamp):
            """
            Process a single timestamp: extract path points, compute speed and other metrics.
            Returns v_p_entry which is a list of the extracted path points and other metrics.
            """
            cur_path, carpose_path = self.pathobj.get_path_in_world_coordinates(timestamp)
            speed = self.pathobj.get_current_speed(timestamp)
            
            # Extract path points at the timestamp
            extracted_points = self.extract_path_points_at_timestamp(cur_path, timestamp, speed, self.delta_t_sec, self.pts_before, self.pts_after)
            if extracted_points.empty:
                return None, None

            v_p_entries = []
            for i in range(len(extracted_points)):
                x = extracted_points.iloc[i]['x']
                y = extracted_points.iloc[i]['y']
                # Collect other data (some of these might not be directly available)
                yaw_angle_rad = carpose_path.theta() 
                curvature = np.nan    
                acceleration = np.nan 
                jerk = np.nan 
                # ... and so on for other quantities

                v_p_entry = [
                    x, y, idx, timestamp, speed, yaw_angle_rad, curvature, acceleration,
                    jerk,  # jerk
                    np.nan,  # longitudinal jerk
                    np.nan,  # lateral jerk
                    np.nan,  # longitudinal acceleration
                    np.nan,  # lateral acceleration
                    np.nan,  # longitudinal velocity
                    np.nan,  # lateral velocity
                    np.nan,  # longitudinal position
                    np.nan,  # lateral position
                    np.nan,  # longitudinal velocity (again?)
                ]
                v_p_entries.append(v_p_entry)

            # Add timestamp index to extracted_points
            extracted_points['timestamp_idx'] = idx
            extracted_points['timestamp'] = timestamp

            return v_p_entries, extracted_points

        # Initialize lists to collect data
        v_p_list = []
        df_virt_path_list = []

        # Get all timestamps from PathTrajectory
        timestamps = self.time_data

        # Use ThreadPoolExecutor for parallel processing
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit tasks for each timestamp
            future_to_timestamp = {executor.submit(process_timestamp, idx, timestamp): timestamp for idx, timestamp in enumerate(timestamps)}
            
            # Process the results as they complete
            for future in as_completed(future_to_timestamp):
                result = future.result()
                if result is not None:
                    v_p_entries, extracted_points = result
                    if v_p_entries:
                        v_p_list.extend(v_p_entries)
                    if not extracted_points.empty:
                        df_virt_path_list.append(extracted_points)

        # Convert lists to DataFrame and array
        df_virt_path = pd.concat(df_virt_path_list, ignore_index=True) if df_virt_path_list else pd.DataFrame()
        v_p = np.array(v_p_list) if v_p_list else np.array([])

        return df_virt_path, v_p
     
    def run(self):
        """ Run the path regressor. """
        # Extract key points from the path data
        self.df_key_points = self.extract_key_points()
        
        # Generate a an equivalent trajectory from the the extracted points
        self.df_trajectory = self.generate_trajectory(self.df_key_points)
        
        # Evaluate KPI of the generated trajectory
        self.kpi = self.evaluate_kpi(self.df_trajectory)
        
        return self.df_key_points, self.df_trajectory, self.kpi
    
    def save(self):
            """ Save the path regressor. """
            repr_str = repr(self).replace(" ", "_").replace(",", "").replace("=", "_").replace("(", "").replace(")", "")
            with open(os.path.join(self.CACHE_DIR, f'df_key_points_{repr_str}.pkl'), 'wb') as f:
                pickle.dump(self.df_key_points, f)
            with open(os.path.join(self.CACHE_DIR, f'df_trajectory_{repr_str}.pkl'), 'wb') as f:
                pickle.dump(self.df_trajectory, f)
            with open(os.path.join(self.CACHE_DIR, f'kpi_{repr_str}.pkl'), 'wb') as f:
                pickle.dump(self.kpi, f)
            
            return self.df_key_points, self.df_trajectory, self.kpi

    def load(self):
        """ Load the path regressor. """
        repr_str = repr(self).replace(" ", "_").replace(",", "").replace("=", "_").replace("(", "").replace(")", "")
        with open(os.path.join(self.CACHE_DIR, f'df_key_points_{repr_str}.pkl'), 'rb') as f:
            self.df_key_points = pickle.load(f)
        with open(os.path.join(self.CACHE_DIR, f'df_trajectory_{repr_str}.pkl'), 'rb') as f:
            self.df_trajectory = pickle.load(f)
        with open(os.path.join(self.CACHE_DIR, f'kpi_{repr_str}.pkl'), 'rb') as f:
            self.kpi = pickle.load(f)
        
        return self.df_key_points, self.df_trajectory, self.kpi

    def get_virtual_path(self):
        """ Get the virtual path. """
        # Extract path points at each timestamp in parallel
        df_virt_path, v_p = self.extract_virtual_path_parallel()
        
        return df_virt_path, v_p
    
    def __repr__(self):
        return f'PathRegressor(path_trajectory={self.pathobj}, carpose={self.carpose}, CACHE_DIR={self.CACHE_DIR}, num_points={self.num_points})'
    
    def __str__(self):
        return f'PathRegressor(path_trajectory={self.pathobj}, carpose={self.carpose}, CACHE_DIR={self.CACHE_DIR}, num_points={self.num_points})'
    
    def plot(self):
        """ Plot the path regressor. """
        # Plot the path regressor
        self.pathobj.plot(self.df_key_points, self.df_trajectory)
        
        return self.df_key_points, self.df_trajectory, self.kpi 
    
    def __repr__(self):
        return f'PathRegressor(path_trajectory={self.pathobj}, carpose={self.carpose}, CACHE_DIR={self.CACHE_DIR})'
    
    def __str__(self):
        return f'PathRegressor(path_trajectory={self.pathobj}, carpose={self.carpose}, CACHE_DIR={self.CACHE_DIR})' 
    
    
    