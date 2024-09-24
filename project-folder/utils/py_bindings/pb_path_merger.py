import os
import sys

# Adjust the path to import se2_function
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.insert(0, parent_dir)

from utils.path_aux_utils import *
from utils.init_utils import pre_required_install_check
# check if the required packages are installed and install them if not
pre_required_install_check()

import matplotlib
matplotlib.use('TkAgg')  # or another GUI backend like 'Qt5Agg'

import matplotlib.pyplot as plt
from numpy.random import default_rng
import numpy as np
from typing import Optional
from spatialmath import SE2

from utils.aidriver_logs_readers.path_loader_utils import *
from utils.se2_function import *
from utils.path_geom_utils import * 
from utils.path_aux_utils import *
from utils.plot_helpers import path_merger_plot, path_merger_plot_cpp
from path_merger.path_merger_utils import PathMergerOptions, path_merger_wrapper
from path_merger.PathMerger import PathMerger
from py_sim.sim_path_merger import path_pre_processing
# %%
BUILD_PATH = '/opt/imagry/aidriver_new/cmake-bin/modules/planner/tools/pybind11_projects/py_path_merger'
if BUILD_PATH not in sys.path:
    sys.path.append(BUILD_PATH)
import libpy_aidriver_path_merger as pm

# Set the path to the data directory 
# IMPORTANT: In general, the data should not be stored in /opt/imagry/aidriver_new
INPUT_DATA_PATH = '/opt/imagry/aidriver_new/modules/planner/tools/pybind11_projects/py_path_merger/data'
# %%
#%% Path merger example
def test_path_merger_wrapper():
#  Example code to test the path merger wrapper
    
    # Generate data in world coordinates for two consecutive frames
    x1 = np.hstack((np.arange(0,1,0.1), np.arange(1.05,20,1)))
    y1_ = lambda x1: 9 * (x1 ** 0.4)
    X_1_world, _, _, p1_world, p1_p1 = path_pre_processing(x1, y1_)
    
    x2 = np.hstack((np.arange(5,6,0.5), np.arange(6.05,30,1)))
    y2_ = lambda x2: 2.5 + 9 * (x2 ** 0.3)
    X_2_world, X_now_world, _, p2_world, p2_p2  = path_pre_processing(x2, y2_)
    
    lm1 = 0.5 #smoothing lambda
    lm2 = 0.5 #derivative constraint lambda
    w_inc = 5 #weighing of p2 before i2 (larger value means faster decay)
    
    # print(dir(libpath_merger))
# %% C++ binding part
    # Initialize the TemporalPathMerger
    path_merger = pm.TemporalPathMerger(tau=0.2, N2=30, lm1=0.5, lm2=0.5, w_inc=5, spline_degree=3, step_size=0.1)
           
    p1_p1_merged_path_cpp = path_merger.merge_paths(
        input_path_ego=p1_p1, 
        car_pose_img=X_1_world.A, 
        car_pose_now=np.identity(3), 
        target_speed_mps=2.7
    )
    p2_p2_merged_path_cpp = path_merger.merge_paths(
        input_path_ego=p2_p2, 
        car_pose_img=X_2_world.A, 
        car_pose_now=X_now_world.A, 
        target_speed_mps=2.7
    )
    
    #%% Plots
    p2_p2_merged_cpp = np.array(p2_p2_merged_path_cpp)
    p2_p2_world_merged_cpp = apply_se2_transform(X_2_world, p2_p2_merged_cpp)
    
    path_merger_plot_cpp(X_1_world, X_2_world, X_now_world, p1_world, p2_world, p2_p2_world_merged_cpp)
    
    # Providing specific arguments
    plt.savefig('modules/planner/tools/pybind11_projects/py_path_merger/src/python/figures/'+'cpp_output_figure.png')

    
# %%
    
if __name__ == '__main__':
    test_path_merger_wrapper()  
# %%
