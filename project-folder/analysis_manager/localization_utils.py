# localization utils
from utils.spatial_poses.se2_function  import *
from scipy.interpolate import interp1d
import numpy as np
import matplotlib.pyplot as plt
from spatialmath import SE2
from spatialmath.base import *

def SE2_transform_world_to_ego(ego_x, ego_y, ego_yaw, P_world):
    """P_world is Nx2 vector of 2d points in world frame"""
    
    # Create the SE(2) matrix for the ego vehicle
    X_ego = SE2(ego_x, ego_y, ego_yaw)
        
    # Compute the SE(2) matrix for the transformation from world to ego
    SE2_world_to_ego = X_ego.inv() * P_world
    
    return SE2_world_to_ego

def SE2_transform_ego_to_world(ego_x, ego_y, ego_yaw, P_ego):
    """P_ego is Nx2 vector of 2d points in ego frame"""
    
    # Create the SE(2) matrix for the ego vehicle
    X_ego = SE2(ego_x, ego_y, ego_yaw)
    
    P_world = X_ego * P_ego
    
    return P_world
