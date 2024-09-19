import numpy as np
from spatialmath import SE2
from py_utils.se2_function import *

class PathAggregator:
    def __init__(self, car_pose_handle):
        """
        Initializes the PathFollower with the provided parameters.
        
        :param car_pose_handle: Function handle to retrieve the current car pose.
        :type car_pose_handle: function        
        :return: None
        """
        self.car_pose_handle = car_pose_handle
        self.Gamma = [] # Aggregated path
        self.Chi = [] # Frame indices associated with the aggregated path
        self.Xi = SE2() # Pose associated with frame according to image time stamp 
        self.frame_count = 0
        self.Ft = []
        
    def get_current_pose_world(self, t):
        """
        Retrieves the current pose in world coordinates.
        
        :param t: Time or frame at which to get the pose.
        :return: Current pose as SE2 object.
        """
        # This function needs to be implemented based on the specific system's pose retrieval method
        Xc = SE2(self.car_pose_handle(t))
        return Xc

    def world_transform(self, Xi, points):
        """
        Placeholder for the method that applies the world transformation to the selected points.
        
        :param Xi: World transformation matrix.
        :param points: List of points to transform (numpy array).
        :return: Transformed points (numpy array).
        """
        # This function needs to be implemented based on the specific system's world transformation method
        points_world = apply_se2_transform(Xi, points)
        return points_world

    def update_path_frame(self, Pi, Xi, Fti):
        """
        Updates Gamma and Chi based on the current frame index i.
        
        :param i: Current frame index.
        :return: Updated Gamma and Chi lists.
        :rtype: list, list
        """        
        self.gamma_c = set()  # Start with an empty set for current active path points
        self.Xi = Xi
        self.frame_count += 1
        self.Ft.append(Fti)
        self.Pi = np.array(Pi)
        
        return

    def find_closest_point(self, pt):
        """
        Returns the index and the point in `path` that is closest to the given point `pt`.

        Parameters:
        - pt (numpy.ndarray): Single point (array of shape (D,)) to find the closest point to.

        Returns:
        - closest_index (int): Index of the closest point in `path`.
        - closest_point (numpy.ndarray): The closest point in the `path`.
        """
        # Calculate distances from pt to each point in path
        distances = np.linalg.norm(self.Pi - pt, axis=1)
        
        # Find the index of the closest point
        closest_index = np.argmin(distances)
        
        # Get the closest point
        closest_point = self.Pi[closest_index]
        
        return closest_index, closest_point
    
    def update_aggregated_path(self, t):
        """        
        build the aggregated path by adding the closest point to the current pose in the path
        
        :param t: Time or frame at which to update the aggregated path.
        :return: None
        """
        Xc = self.get_current_pose_world(t)
        # Find the closest point in P_c to X_c
        j_min, p_min = self.find_closest_point(Xc.t)
        p_min = p_min.reshape(1, -1)
        self.gamma_c.add(j_min)  # Add the index of the closest point to gamma_c

        # Apply world transformation to the selected path points
        tilde_P_i = self.world_transform(self.Xi, p_min)

        # Update Gamma and Chi
        self.Gamma.append(tilde_P_i)
        self.Chi.append(self.frame_count)

        return 
    
    def get_aggregated_path(self):
        """
        Returns the aggregated path.
        
        :return: Aggregated path.
        """
        agg_path = np.asarray(self.Gamma).reshape(-1, 2)
        add_coloring_indices = np.asarray(self.Chi)
        return agg_path, add_coloring_indices
