import math
import numpy as np
from py_utils.aidriver_logs_readers.path_loader_utils import *
from py_utils.se2_function import *
from py_utils.path_aux_utils import *
import matplotlib.pyplot as plt

def compute_tangent_to_path_at_index(p, i, normalize=False):
    """
    Compute the numerical tangent of a 2D curve at a given index using finite differences.

    :param x: Array of x coordinates of the curve.
    :param y: Array of y coordinates of the curve.
    :param i: Index at which to compute the tangent.
    :return: The tangent vector as (dx, dy).
    """
    
    x= p[:,0]
    y= p[:,1]
    
    n = len(x)
    
    if i < 0 or i >= n:
        raise ValueError("Index out of range.")

    if i == 0:
        # Forward difference for the first point
        dx = x[i+1] - x[i]
        dy = y[i+1] - y[i]
    elif i == n-1:
        # Backward difference for the last point
        dx = x[i] - x[i-1]
        dy = y[i] - y[i-1]
    else:
        # Central difference for interior points
        dx = (x[i+1] - x[i-1]) / 2.0
        dy = (y[i+1] - y[i-1]) / 2.0
        
    if normalize:
        norm = math.sqrt(dx**2 + dy**2)
        dx /= norm
        dy /= norm  
    
    tan_vector = np.array([dx, dy])
    theta_rad = math.atan2(dy, dx)
    
    return tan_vector, theta_rad

def compute_derivative_at_k(points, k):
    x = points[:, 0]
    y = points[:, 1]

    if k <= 0 or k >= len(points) - 1:
        raise ValueError("k must be within the range 1 to len(points) - 2")

    dx = (x[k + 1] - x[k - 1]) / 2
    dy = (y[k + 1] - y[k - 1]) / 2

    return dx, dy

def plot_points_and_derivatives(points):
    x = points[:, 0]
    y = points[:, 1]

    # Compute derivatives for each point
    derivatives = np.array([compute_derivative_at_k(points, k) for k in range(1, len(points) - 1)])

    # Plot original points
    plt.scatter(x, y, color='blue', label='Points')

    # Plot derivatives as arrows
    for k in range(1, len(points) - 1):
        dx, dy = derivatives[k - 1]
        plt.arrow(x[k], y[k], dx, dy, head_width=0.1, head_length=0.1, fc='red', ec='red')

    plt.xlabel('x')
    plt.ylabel('y')
    plt.title('Points and their Derivatives')
    plt.legend()
    plt.grid()
    plt.show()

# # Example usage
# points = np.array([[0, 0], [1, 2], [2, 3], [3, 5], [4, 4]])
# plot_points_and_derivatives(points)


def find_closest_point(path, position):
    closest_point = None
    closest_distance = float('inf')
    closest_index = None

    for i, point in enumerate(path):
        x, y = point
        dx = x - position[0, 2]
        dy = y - position[1, 2]
        distance = math.sqrt(dx**2 + dy**2)

        # Check if the point is in front of the position
        u = position[:2, 0]
        # angle = math.atan2(u[1, 0], u[0, 0])
        # u = np.array([math.cos(angle), math.sin(angle)])
        v = point - position[:2, 2]
        uv = np.dot(u, v)
        if uv >= 0 and distance < closest_distance:
            closest_point = point
            closest_distance = distance
            closest_index = i

    return closest_point, closest_index

# %%
def get_proj_idx(path_1, path_2, clean=False):
    """
    Returns the indices of the closest points in `path_2` for each point in `path_1`.

    Parameters:
    - path_1 (numpy.ndarray): Array of shape (N, D) representing the coordinates of points in path 1.
    - path_2 (numpy.ndarray): Array of shape (M, D) representing the coordinates of points in path 2.
    - clean (bool): If True, removes duplicate indices.

    Returns:
    - idx (list): List of indices representing the closest points in `path_2` for each point in `path_1`.
    """
    idx = [np.linalg.norm(path_2 - p, axis=1).argmin() for p in path_1]
    idx.sort()
    if clean:
        idx = np.unique(idx)
    return idx


def getProj(p1, p2):
    """
    Calculates the projections of two paths onto each other.

    Args:
        p1 (list): The first path.
        p2 (list): The second path.

    Returns:
        tuple: A tuple containing the projections of p1 and p2 onto each other, as well as the indices of the projections.

    """
    idx1 = get_proj_idx(p2, p1, clean=True)
    proj1 = np.array(get_path_by_idx(p1, idx1))
    idx2 = get_proj_idx(proj1, p2)
    proj2 = np.array(get_path_by_idx(p2, idx2))

    return proj1, proj2, idx1, idx2

def find_close_pt_to_path(P, X):
    """
    Finds the closest point in the given path to a given point.

    Parameters:
    X (float): The point to find the closest point to.
    P (numpy.ndarray): The path to search for the closest point.

    Returns:
    tuple: A tuple containing the closest point and its index in the path.
    """
    X = X.squeeze()
    for i, p in enumerate(P):        
        u = P[i+1] - P[i]
        v = X-p
        u_dot_v = np.dot(u, v)
        if u_dot_v <= 0:
            return p, i


def extract_blend_regions(x_hat_prev, x_i, s_i, w, K_s):
    """
    Defines blending regions and extracts relevant parts from x_hat_(i-1) and x_i.

    Parameters:
    x_hat_prev (numpy.ndarray): The previous path x_hat_(i-1).
    x_i (numpy.ndarray): The new path x_i.
    s_i (int): The start index of the blend region.
    w (int): The width of the blend region.
    K_s: number of indexes to skip w.r.t. the new path x_i
    Returns:
    tuple: A tuple containing the blended region r_1 and the extracted region r_2.
    """
    r_1 = x_hat_prev[s_i-w : s_i+w+1]
    r_2 = x_i[K_s : K_s+w+1]
    return r_1, r_2

def blend_paths(x_hat_prev, x_i, s_i, w, K_s):
    """
    Blends the previous path x_hat_(i-1) and the new path x_i.

    Parameters:
    x_hat_prev (numpy.ndarray): The previous path x_hat_(i-1).
    x_i (numpy.ndarray): The new path x_i.
    s_i (int): The start index of the blend region.
    w (int): The width of the blend region.
    K_s: number of indexes to skip w.r.t. the new path x_i

    Returns:
    numpy.ndarray: The blended path X+hat_i.
    """
    # r_1, r_2 = extract_blend_regions(x_hat_prev, x_i, s_i, w, K_s)
    
    # Blend the paths
    p1_end = x_hat_prev[s_i]
    p2_start = x_i[0]
    blended_path = polynomial_blending(p1_end, p2_start)
    
    # Update world path and ego position
    world_path = np.vstack((x_hat_prev, blended_path, x_i))
    return blended_path

# Function to interpolate pose at a given time
def interpolate_pose(t, poses_table):
    times = poses_table[:, 0]
    x_interp = interp1d(times, poses_table[:, 1], kind='linear')
    y_interp = interp1d(times, poses_table[:, 2], kind='linear')
    theta_interp = interp1d(times, poses_table[:, 3], kind='linear')
    x = x_interp(t)
    y = y_interp(t)
    theta = theta_interp(t)
    return np.array([x, y, theta])

def extract_path_poses(trip_path, df_xyz_NED):
    df_imu = read_nissan_imu_data(trip_path)
    yaw = np.asarray(df_imu['yaw'])
    t_yaw = np.asarray(df_imu['time_stamp'])
    
    df_xyz = df_xyz_NED

    x_ego = df_xyz['x']
    y_ego = df_xyz['y']
    t_ego = df_xyz['time_stamp']
    x_path,y_path,t_path,v_ego = read_path_data(trip_path)
    
    plot_poses = False
    if plot_poses:
        ds_factor = 100
        plot_se2_path(x_ego[::ds_factor], y_ego[::ds_factor], yaw[::ds_factor])


    print_rect_path = False
    if print_rect_path:
        with plt.ioff():
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(5, 2.7))
            my_plotter(ax1, x_ego, y_ego, {'color':'orange', 'linewidth':1, 'linestyle':'--','label':'ego'})
        # my_plotter(ax2, u, v, {'color':'red', 'linewidth':1, 'linestyle':'--','label':'NED'})
            ax1.set_title('EgoPlot')
        # ax2.set_title('NED')
            ax1.set_aspect('equal', 'box')
        # ax2.set_aspect('equal', 'box')
        pan_handler = panhandler(fig)       
        plt.show()

    # Get SE(2) matrices for each P_time_stamp
    SE2_matrices, lambda_handler_ego = get_interpolated_pose_SE2(t_path, yaw, t_yaw, x_ego, y_ego, t_ego)
    return SE2_matrices, x_path, y_path, t_path, lambda_handler_ego

def transform_path(p1, pose_1, pose_2):
    theta_1, x_1, y_1 = pose_1[2], pose_1[0], pose_1[1]
    theta_2, x_2, y_2 = pose_2[2], pose_2[0], pose_2[1]

    # Transformation matrix from pose_1 to pose_2
    dx, dy = x_2 - x_1, y_2 - y_1
    dtheta = theta_2 - theta_1

    T = np.array([
        [np.cos(dtheta), -np.sin(dtheta), dx],
        [np.sin(dtheta), np.cos(dtheta), dy],
        [0, 0, 1]
    ])

    # Transform path p1
    p1_homogeneous = np.hstack((p1, np.ones((p1.shape[0], 1))))
    p1_transformed = (T @ p1_homogeneous.T).T[:, :2]
    return p1_transformed

def polynomial_blending(p1_end, p2_start, num_points=100):
        """
        Creates a smooth polynomial blend between the end of p1 and the start of p2.
        """
        A = np.array([
            [0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1],
            [0, 0, 0, 0, 1, 0],
            [5, 4, 3, 2, 1, 0],
            [0, 0, 0, 2, 0, 0],
            [20, 12, 6, 2, 0, 0]
        ])
        
        b_x = np.array([p1_end[0], p2_start[0], 0, 0, 0, 0])
        b_y = np.array([p1_end[1], p2_start[1], 0, 0, 0, 0])
        
        coeffs_x = np.linalg.solve(A, b_x)
        coeffs_y = np.linalg.solve(A, b_y)
        
        t = np.linspace(0, 1, num_points)
        x_blend = np.polyval(coeffs_x[::-1], t)
        y_blend = np.polyval(coeffs_y[::-1], t)
        
        return np.vstack((x_blend, y_blend)).T

