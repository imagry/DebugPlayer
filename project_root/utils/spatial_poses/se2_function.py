# se2_function.py
import numpy as np
from scipy.interpolate import interp1d
import numpy as np
from spatialmath import SE2



def get_interpolated_pose(P_time_stamp, yaw, time_stamp_yaw, ego_x, ego_y, ego_time_stamp):
    # Ensure all inputs are numpy arrays
    P_time_stamp = np.array(P_time_stamp)
    yaw = np.array(yaw)
    time_stamp_yaw = np.array(time_stamp_yaw)
    ego_x = np.array(ego_x)
    ego_y = np.array(ego_y)
    ego_time_stamp = np.array(ego_time_stamp)

    # Interpolators for ego_x, ego_y, and yaw
    ego_x_interpolator = interp1d(ego_time_stamp, ego_x, fill_value="extrapolate")
    ego_y_interpolator = interp1d(ego_time_stamp, ego_y, fill_value="extrapolate")
    yaw_interpolator = interp1d(time_stamp_yaw, yaw, fill_value="extrapolate")

    # Interpolate ego_x, ego_y, and ego_yaw for each P_time_stamp
    interpolated_ego_x = ego_x_interpolator(P_time_stamp)
    interpolated_ego_y = ego_y_interpolator(P_time_stamp)
    interpolated_ego_yaw = yaw_interpolator(P_time_stamp)

    # Create the result array
    interpolated_pose = np.vstack((P_time_stamp, interpolated_ego_x, interpolated_ego_y, interpolated_ego_yaw)).T

    return interpolated_pose

def compute_se2_matrix(time_stamp, ego_x_interpolator, ego_y_interpolator, yaw_interpolator):
    # Interpolate ego_x, ego_y, and ego_yaw for the given time stamp
    interpolated_ego_x = ego_x_interpolator(time_stamp)
    interpolated_ego_y = ego_y_interpolator(time_stamp)
    interpolated_ego_yaw = yaw_interpolator(time_stamp)

    # Compute the SE(2) matrix
    SE2_matrix = np.array([
        [np.cos(interpolated_ego_yaw), -np.sin(interpolated_ego_yaw), interpolated_ego_x],
        [np.sin(interpolated_ego_yaw), np.cos(interpolated_ego_yaw), interpolated_ego_y],
        [0, 0, 1]
    ])

    return SE2_matrix
    
def get_interpolated_pose_SE2(P_time_stamp, yaw, time_stamp_yaw, ego_x, ego_y, ego_time_stamp):
    # Ensure all inputs are numpy arrays
    P_time_stamp = np.array(P_time_stamp)
    yaw_rad = np.deg2rad(np.array(yaw))
    time_stamp_yaw = np.array(time_stamp_yaw)
    ego_x = np.array(ego_x)
    ego_y = np.array(ego_y)
    ego_time_stamp = np.array(ego_time_stamp)

    # Create Interpolators (objects) for ego_x, ego_y, and yaw to be used later for other time stamps
    ego_x_interpolator = interp1d(ego_time_stamp, ego_x, fill_value="extrapolate")
    ego_y_interpolator = interp1d(ego_time_stamp, ego_y, fill_value="extrapolate")
    yaw_interpolator = interp1d(time_stamp_yaw, yaw_rad, fill_value="extrapolate")

    # Interpolate ego_x, ego_y, and ego_yaw for each P_time_stamp
    interpolated_ego_x =   ego_x_interpolator(P_time_stamp)
    interpolated_ego_y =   ego_y_interpolator(P_time_stamp)
    interpolated_ego_yaw = yaw_interpolator(P_time_stamp)

    # Create SE(2) matrices
    SE2_matrices = []
    for x, y, theta in zip(interpolated_ego_x, interpolated_ego_y, interpolated_ego_yaw):
        SE2_matrix = np.array([
            [np.cos(theta), -np.sin(theta), x],
            [np.sin(theta), np.cos(theta), y],
            [0, 0, 1]
        ])
        SE2_matrices.append(SE2_matrix)
       
    lambda_handler_ego = lambda time_stamp: compute_se2_matrix(time_stamp, ego_x_interpolator, ego_y_interpolator, yaw_interpolator)

    return SE2_matrices, lambda_handler_ego

def inverse_se2_matrix(se2_matrix):
    # Extract the rotation and translation components
    R = se2_matrix[:2, :2]
    t = se2_matrix[:2, 2]
    
    # Compute the inverse rotation (transpose of the rotation matrix)
    R_inv = R.T
    
    # Compute the inverse translation
    t_inv = -np.dot(R_inv, t)
    
    # Construct the inverse SE(2) matrix
    se2_matrix_inv = np.eye(3)
    se2_matrix_inv[:2, :2] = R_inv
    se2_matrix_inv[:2, 2] = t_inv
    
    return se2_matrix_inv

# Function to compute SE(2) transformation
def apply_se2_transform(se2_matrix, points):
    
    # if given as list convert to numpy array
    if isinstance(points, list):
        points = np.array(points)
        
    # check points.shape and transpose if required
    if points.shape[0] == 2:
        points = points.T
        
    #check if need to squeeze points
    if points.shape[1] == 1:
        points = np.squeeze(points)

    # check if se_matrix is given in class SE2 and obtain matrix if so
    if isinstance(se2_matrix, SE2):
        se2_matrix = se2_matrix.A   
                        
    # Convert points to homogeneous coordinates
    points_homogeneous = np.hstack((points, np.ones((points.shape[0], 1))))
    transformed_points_homogeneous = (se2_matrix @ points_homogeneous.T).T
    transformed_points = transformed_points_homogeneous[:, :2]
    
    # check if points were given as list and return as list
    if isinstance(points, list):
        transformed_points = transformed_points.tolist()
        
    return transformed_points

# function to apply SE(2) to a series of SE(2) matrices
def apply_se2_transform_to_series(T, se2_matrices):
    # Apply the SE(2) transformation to each SE(2) matrix
    transformed_se2_matrices = [T @ se2_matrix_i for se2_matrix_i in se2_matrices]
        
    return transformed_se2_matrices
    

