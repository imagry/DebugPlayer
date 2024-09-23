import os
import sys

# Adjust the path to import se2_function
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.insert(0, parent_dir)

from utils.path_aux_utils import *
# check if the required packages are installed and install them if not
pre_required_install_check()

import matplotlib
matplotlib.use('TkAgg')  # or another GUI backend like 'Qt5Agg'


import numpy as np
from spatialmath import SE2
import matplotlib.pyplot as plt
from utils.se2_function import *
from utils.path_aux_utils import *
from path_merger.path_merger_utils import * 
from utils.plot_helpers import * 
from path_merger.PathMerger import PathMerger

#%% test_path_merger_wrapper
def test_path_merger_wrapper():
#  Example code to test the path merger wrapper
    
    # Generate data in world coordinates for three consecutive frames
    x1 = np.hstack((np.arange(0,1,0.01), np.arange(1.05,20,0.5)))
    y1_ = lambda x1: 9 * (x1 ** 0.4)
    X_1_world, _, _, p1_world, p1_p1 = path_pre_processing(x1, y1_)
    
    x2 = np.hstack((np.arange(5,6,0.01), np.arange(6.05,30,0.5)))
    y2_ = lambda x2: 2.5 + 9 * (x2 ** 0.3)
    X_2_world, X_now_world, _, p2_world, p2_p2  = path_pre_processing(x2, y2_)
    
    lm1 = 0.5 #smoothing lambda
    lm2 = 0.5 #derivative constraint lambda
    w_inc = 5 #weighing of p2 before i2 (larger value means faster decay)

    # Prepare data for path_merger_wrapper: bring p1 and p2 to the ego coordinates of p2
    p1_p2 = apply_se2_transform(X_2_world.inv(), p1_world)
    
                    
    p2_merged_ego_p2_truncated, p2_merged_world, i0, i1, i12, i2 = path_merger_wrapper(p1_p2, p2_p2, X_1_world, X_2_world, X_now_world, tau_1= 0.2, N2=30,
                                                options=PathMergerOptions(lambda_1= lm1, lambda_2=lm2, w=w_inc), DEBUG_MODE = True)                              

    path_merger_plot(X_1_world, X_2_world, X_now_world, p1_world, p2_world, p2_merged_world, i0, i1, i12, i2, p2_merged_ego_p2_truncated, p1_p2, p2_p2)
    plt.savefig('modules/planner/tools/pybind11_projects/py_path_merger/src/python/figures/'+'func_output_figure.png')

    return()


def test_PathMergerClass():
    # Generate data in world coordinates for three consecutive frames
    x1 = np.hstack((np.arange(0,1,0.01), np.arange(1.05,20,0.5)))
    y1_ = lambda x1: 9 * (x1 ** 0.4)
    X_1_world, _, _, p1_world, p1_p1 = path_pre_processing(x1, y1_)
    
    x2 = np.hstack((np.arange(5,6,0.01), np.arange(6.05,30,0.5)))
    y2_ = lambda x2: 2.5 + 9 * (x2 ** 0.3)
    X_2_world, X_now_world, _, p2_world, p2_p2  = path_pre_processing(x2, y2_)
    
    lm1 = 0.5 #smoothing lambda
    lm2 = 0.5 #derivative constraint lambda
    w_inc = 5 #weighing of p2 before i2 (larger value means faster decay)
    
    # Test the Class version
    # instantiate PathMerger class
    path_merger = PathMerger(tau_1_ms=0.2, N2=30, lambda_1=lm1, lambda_2=lm2, w=w_inc, spline_degree=3, DEBUG_MODE=True)
    
    # feed it the first path p1_p1
    p1_p1_merged = path_merger.merge_with_new_path(p1_p1, X_1_world, None)
    
    # feed it with the second path p2_p2
    p2_p2_merged = path_merger.merge_with_new_path(p2_p2, X_2_world, X_now_world)
    
    # plot the merged path
    p2_merged_world = apply_se2_transform(X_2_world, p2_p2_merged)
    p1_p2 = apply_se2_transform(X_2_world.inv(), p1_world)
    history = path_merger.history
    i0, i1, i12, i2 = history.iloc[-1][3:]
    path_merger_plot(X_1_world, X_2_world, X_now_world, p1_world, p2_world, p2_merged_world, i0, i1, i12, i2, p2_p2_merged, p1_p2, p2_p2)
    plt.savefig('modules/planner/tools/pybind11_projects/py_path_merger/src/python/figures/'+'class_output_figure.png')

    return()
     
def fit_bspline(p):
    # Fit a Bspline to the generated paths p1 and p2
    # Return the fitted Bspline object and the resampled path
    
    # fit spline to each of the paths
    p_spline_obj, _ = FitSpline(p, k=3, lm=0)  
    p_resampled = np.asarray(interpolate.splev(np.linspace(0,1,101),p_spline_obj)).T    
    
    return p_spline_obj, p_resampled

def path_pre_processing(x, y_):
    
    # Convert x and y coordinates to a numpy array    
    p_world = np.array([x, y_(x)]).T

    # fit spline to each of the paths
    p_world_spline, _ = FitSpline(p_world, k=3, lm=0)
    
    p_world_sampled = np.asarray(interpolate.splev(np.linspace(0,1,101),p_world_spline)).T
    
    # Compute the tangent and angle 
    tang_1, theta_rad = compute_tangent_to_path_at_index(p_world_sampled,0, normalize = True)

    # Create an SE2 object representing the initial pose
    X_world = SE2(x=p_world_sampled[0, 0], y=p_world_sampled[0, 1], theta=theta_rad)
    
    # Transform the spline path to the ego frame
    p_ego_sampled = apply_se2_transform(X_world.inv(), p_world_sampled)
    
    p_ego_spline, _ = FitSpline(p_ego_sampled, k=3, lm=0)    

    X_now = SE2(x = x[1], y=y_(x[1]), theta= X_world.xyt()[2])

    return X_world, X_now, p_ego_spline, p_world_sampled, p_ego_sampled

def test_path_merger_function_with_Spline_fit():
    # Generate data in world coordinates
    x1 = np.arange(0,20,0.1)
    y1 = 9*(x1**0.4)

    x2 = np.arange(5,30,0.1)
    y2 = 2+9*(x2**0.3)

    p1_world = np.array([x1,y1]).T
    p2_world = np.array([x2,y2]).T

    # Fit Bspline to p1 and p2    
    bspline_p1, p1_world_resampled = fit_bspline(p1_world)
    bspline_p2, p2_world_resampled = fit_bspline(p2_world)

    lm1 = 0.5 #smoothing lambda
    lm2 = 0.5 #derivative constraint lambda
    w_inc = 5 #weighing of p2 before i2 (larger value means faster decay)

    tang_1, theta_rad_1 = compute_tangent_to_path_at_index(p1_world_resampled,0, normalize = True)

    X_1_world = SE2( x= p1_world_resampled[0,0], y = p1_world_resampled[0,1], theta =theta_rad_1)
    print('Spline: X_1_world:', X_1_world.xyt())
    tang_2, theta_rad_2 = compute_tangent_to_path_at_index(p2_world_resampled,0, normalize = True)

    X_2_world = SE2( x= p2_world_resampled[0,0], y = p2_world_resampled[0,1], theta =theta_rad_2)
    print('Spline: X_2_world:', X_2_world.xyt())
    X_now_world = SE2( x=7, y= 17.5, theta = np.pi/4)
    print('Spline: X_now_world:', X_now_world.xyt())
    p1_ego_p1 = apply_se2_transform(X_1_world.inv(), p1_world_resampled)
    p1_ego_p2 = apply_se2_transform(X_2_world.inv(), p1_world_resampled)
    T_12 = X_1_world.inv() * X_2_world
    
    p1_ego_p2_ = apply_se2_transform(T_12.inv(), p1_ego_p1)
    print(f"p1_p2_from_world:\n {p1_ego_p2[0:10,:]}")
    print(f"p1_p2 from p1_p1 :\n {p1_ego_p2_[0:10,:]}")
    print('T_21:', T_12.inv().xyt())

    p2_ego_p2 = apply_se2_transform(X_2_world.inv(), p2_world_resampled)
    
    
    # Merge paths 
    p2_merged_ego_p2_truncated, p2_merged_world, i0, i1, i12, i2 = path_merger_wrapper(p1_ego_p2,p2_ego_p2,X_1_world, X_2_world, 
                                                                                       X_now_world, tau_1= 0.2, N2=30, options=PathMergerOptions(lambda_1= 0.5, lambda_2=0.5, w=4), DEBUG_MODE = True)                              

    path_merger_plot(X_1_world, X_2_world, X_now_world, p1_world_resampled, p2_world_resampled, p2_merged_world, i0, i1, i12, i2, p2_merged_ego_p2_truncated, p1_ego_p2, p2_ego_p2)
    plt.savefig('modules/planner/tools/pybind11_projects/py_path_merger/src/python/figures/'+'spline_output_figure.png')

    return()

                                     
#%% main
# def main():
#     test_path_merger_wrapper()

if __name__ == "__main__":

    # test_PathMergerClass()
    test_path_merger_wrapper()
    
    # test_path_merger_function_with_Spline_fit()
