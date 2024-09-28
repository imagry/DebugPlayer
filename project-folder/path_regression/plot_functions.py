# plot_functions.py
import pyqtgraph as pg
import numpy as np
from prg_utils import get_color_list
from DataClasses.PathRegressor import PathRegressor


# Function to update the plot when controls change
def update_plot(ui_elements , prg_obj1: PathRegressor, prg_obj2: PathRegressor = None):
    plt = ui_elements['plt']
    plt.clear()
    # Re-plot the car pose trajectory
    df_car_pose = prg_obj1.get_carpose()
    plt.plot(df_car_pose['cp_x'].T, df_car_pose['cp_y'].T, pen=pg.mkPen(width=1), symbol='star', symbolBrush='b', symbolSize= 2)

    # Get plot settings 
    line_width = ui_elements['line_width_spin'].value()
    marker_size = ui_elements['marker_size_spin'].value()
    colors_num = ui_elements['colors_num_spin'].value()  
    colors_palette_list = ui_elements['colors_palette_list']
    
    # Get the selected colors palette         
    palette = [item.text() for item in colors_palette_list.selectedItems()]
    if len(palette) == 0:
        palette = ['r', 'g', 'b', 'c', 'm', 'y', 'k', 'w']
                               
    # Recalculate virtual path
    df_virt_path1, v_p1 = prg_obj1.get_virtual_path()

    if v_p1 is None: # If the virtual path is not calculated, return
        return
    
    # Re-plot virtual path points
    if v_p1.size > 0:
        x1_vp = v_p1[:,0]
        y1_vp = v_p1[:,1]
        timestamp_idxs1 = v_p1[:,2]

    # Plot v_p1
    plot_path_with_colors(x1_vp, y1_vp, ui_elements, path_symbol='o')
    
    if prg_obj2 is None:
        return
    
    df_virt_path2, v_p2 = prg_obj2.get_virtual_path()
    if v_p2 is None:
        return
    
    if v_p2.size > 0:
        x2_vp = v_p2[:,0]
        y2_vp = v_p2[:,1]
        timestamp_idxs2 = v_p2[:,2]
        
    # Plot v_p2
    plot_path_with_colors(x2_vp, y2_vp, ui_elements, path_symbol='x')
    
    
    
    
        

def calculate_virtual_path(ui_elements, prg_obj1: PathRegressor, prg_obj2: PathRegressor = None):
    # Get updated values
    delta_t_sec_val = float(ui_elements['delta_t_input'].text())
    pts_before_val = ui_elements['pts_before_spin'].value()
    pts_after_val = ui_elements['pts_after_spin'].value()
    colors_num = ui_elements['colors_num_spin'].value()
    
    # Update the PathRegressor object
    params_dict = {'delta_t_sec': delta_t_sec_val, 'pts_before': pts_before_val, 'pts_after': pts_after_val}
    prg_obj1.update_params(params_dict)
    prg_obj1.eval()
    
    # Recalculate virtual path
    v_p = prg_obj1.get_virtual_path()
    
    if prg_obj2 is not None:
        prg_obj2.update_params(params_dict)
        prg_obj2.eval()
        v_p2 = prg_obj2.get_virtual_path()
    
    update_plot(ui_elements, prg_obj1, prg_obj2)

    
    
    
def save_figure(ui_elements):
    """Save the current plot to a file."""
    plt = ui_elements['plt']
    exporter = pg.exporters.ImageExporter(plt.plotItem)
    exporter.parameters()['width'] = 1000
    exporter.export('trajectory_plot.png')

def plot_path_with_colors(x, y, ui_elements, path_symbol='o'):
    """Plot path with colors based on UI inputs."""
    plt = ui_elements['plt']
    line_width = ui_elements['line_width_spin'].value()
    marker_size = ui_elements['marker_size_spin'].value()
    colors_num = ui_elements['colors_num_spin'].value()
    palette = [item.text() for item in ui_elements['colors_palette_list'].selectedItems()]
    if not palette:
        palette = ['r', 'g', 'b', 'c', 'm', 'y', 'k', 'w']
    colors = get_color_list(colors_num, palette)
    for i in range(colors_num):
        mask = np.arange(i, len(x), colors_num)
        plt.plot(x[mask], y[mask], pen=None, symbol=path_symbol, symbolSize=marker_size, symbolBrush=colors[i])

def get_color_list(colors_num, palette):
    """Generate a list of colors based on the number and palette."""
    return palette[:colors_num]


def prepare_plot_data(idx, timestamp_idx, x_vp, y_vp, color):
    """
    Prepare the data for a given timestamp index.
    This function returns the mask and the color.
    """
    mask = timestamp_idx == idx
    return (x_vp[mask], y_vp[mask], color)