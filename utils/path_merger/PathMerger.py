# %% Import libraries
import numpy as np
from scipy.interpolate import BSpline
from typing import Optional
from spatialmath import SE2
from spatialmath.base import *
from scipy import interpolate
from scipy.stats import linregress
from copy import deepcopy
import scipy.linalg as ln
import pandas as pd

import os
import sys

# Adjust the path to import se2_function
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.insert(0, parent_dir)

from utils.se2_function import *
from utils.path_geom_utils import *
from utils.path_aux_utils import *
import path_merger.path_merger_utils as pmrg
from utils.plot_helpers import * 

class PathMerger:
    def __init__(self, tau_1_ms: float = 50, N2: int = 50, lambda_1: float = 0.5, lambda_2: float = 50, w: float = 3, spline_degree: int = 3, DEBUG_MODE: bool = False):        
        """
        Initialize the PathMerger with basic parameters and memory.

        :param tau_1: Time constant to approximate system delay from path handler to control.
        :param N2: Number of points in p2 that should be included in the merged path.
        :param options: Additional options for the path merger.
        """
        self.tau_1_ms = tau_1_ms
        self.N2 = N2
        self.lambda_1 = lambda_1
        self.lambda_2 = lambda_2
        self.w = w
        self.spline_degree = spline_degree
        self.DEBUG_MODE = DEBUG_MODE     
        
        self.p1_p1 = None
        self.X_1_world = None
        # define history for debugging as pandas dataframe with columns: p2_merged_world, X_2_world, X_now_world, i0, i1, i12, i2
        self.history = pd.DataFrame(columns=['p2_merged_world', 'X_2_world', 'X_now_world', 'i0', 'i1', 'i12', 'i2'])
                
    def update_history(self, p2_p2_merged, X_2_world, X_now_world, i0, i1, i12, i2):
        """
        Update the history of the path merger with the current values of the path, poses and indices.

        :param p2_merged_world: The merged path in the world coordinates.
        :param X_2_world: The SE2 object representing the pose of the path in the world coordinates.
        :param X_now_world: The SE2 object representing the current pose of the robot in the world coordinates.
        :param i0: The index of the first point of the path p2 that was included in the merged path.
        :param i1: The index of the last point of the path p2 that was included in the merged path.
        :param i12: The index of the last point of the path p1 that was included in the merged path.
        :param i2: The index of the first point of the path p2 that was included in the merged path.
        """                
        new_row = pd.DataFrame([{
            'p2_merged_world': p2_p2_merged, 
            'X_2_world': X_2_world, 
            'X_now_world': X_now_world, 
            'i0': i0, 
            'i1': i1, 
            'i12': i12, 
            'i2': i2
        }])
        self.history = pd.concat([self.history, new_row], ignore_index=True)

                            
    def merge_with_new_path(self, p2_p2: np.ndarray, X_2_world: SE2, X_now_world: SE2) -> np.ndarray:
        """
        Merge the new path with the previous path.

        :param p2_p2: The new path in the ego coordinates of p2.
        :param X_2_world: The SE2 object representing the pose of the path in the world coordinates.
        :param X_now_world: The SE2 object representing the current pose of the robot in the world coordinates.
        :return: The merged path in the world coordinates.
        """
        # Handling invalid inputs
        if p2_p2 is None:
            raise ValueError("Path p2_p2 is None. Please provide a valid path.")
        if X_2_world is None:
            raise ValueError("Pose X_2_world is None. Please provide a valid pose.")    
        if X_now_world is None and self.p1_p1 is not None:
            raise ValueError("Pose X_now_world is None. Please provide a valid pose.")
        # check p2_p2 is not too short, we need minimal amount of points based on Spline degree to merge
        if len(p2_p2) < self.spline_degree + 1:
            raise ValueError("Path p2_p2 is too short. Please provide a path with at least {} points.".format(self.spline_degree + 1))
        
        
        # On first call, store p2_p2 as the previous path with its corresponding X_2_world and return without merging
        if self.p1_p1 is None:
            self.p1_p1 = p2_p2
            self.X_1_world = X_2_world
            
            if self.DEBUG_MODE:  #update history
                p2_world = apply_se2_transform(X_2_world, p2_p2)
                self.update_history(p2_world, X_2_world, X_now_world, None, None, None, None)
            
            return p2_p2
        
        # transform p1_p1 to ego coordinates of p2
        T_12 = self.X_1_world.inv() * X_2_world
        p1_p2 = apply_se2_transform(T_12.inv(), self.p1_p1)

        # Merge the paths        
        if self.DEBUG_MODE:
            p2_p2_merged_truncated, p2_merged_world, i0, i1, i12, i2 = pmrg.path_merger_wrapper(p1_p2, p2_p2, self.X_1_world, X_2_world, X_now_world, self.tau_1_ms, self.N2, pmrg.PathMergerOptions(lambda_1=self.lambda_1, lambda_2=self.lambda_2, w=self.w), self.DEBUG_MODE)
        else:
            p2_p2_merged_truncated = pmrg.path_merger_wrapper(p1_p2, p2_p2, self.X_1_world, X_2_world, X_now_world, self.tau_1_ms, self.N2, pmrg.PathMergerOptions(lambda_1=self.lambda_1, lambda_2=self.lambda_2, w=self.w), self.DEBUG_MODE)
        
        # update memory
        self.p1_p1 = p2_p2_merged_truncated
        self.X_1_world = X_2_world
        
        if self.DEBUG_MODE: #update history
            self.update_history(p2_merged_world, X_2_world, X_now_world, i0, i1, i12, i2)            
        
        return p2_p2_merged_truncated    
        