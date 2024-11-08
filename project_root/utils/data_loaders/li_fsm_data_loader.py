# %%

# Description: A utility function to read multiple log files to obtain vehicle state
import polars as pl
from datetime import datetime


import polars as pl

#  cruise_control.csv, driving_mode.csv, speed.csv, steering
def read_li_fsm_logs(filepath, log_files_names = None):
    """
    Reads a CSV file with columns structure as follows:
    fixed headers = time_stamp, li_state, path_ts, map_obj_ts
    optional headers = Phi_0, Phi_1, Intent_R, Intent_F, Intent_L, DWB_0, DWB_1, RWB_0, RWB_1, 
                        reached_waiting_box, hit_point_x_ego_frame, hit_point_y_ego_frame, distance, 
                        CEWB_0, CEWB_1, ENLI_1, stop_line_under_the_ego, hit_point_x_ego_frame, 
                        hit_point_y_ego_frame, EXLI_1, RIF_0, RIF_1

    """
    # Read the entire CSV file as a Polars DataFrame
    try:
        df = pl.read_csv(filepath, null_values=[""], truncate_ragged_lines=True)
        # Strip leading and trailing spaces from column names
        df.columns = [col.strip() for col in df.columns]
    except:
        print(f"Error: Could not read the log file {filepath}")
        df = None
            
          
    return df

# %%
if __name__ == '__main__':
    # Test the function
    logs_file_path = "/home/thh3/data/li_conditions_2024-11-07T15_00_53.csv"
    df_li_fsm = read_li_fsm_logs(logs_file_path)
    if df_li_fsm is not None:
        print(df_li_fsm.head())
        print(df_li_fsm.schema)
        
        
from graphviz import Digraph

def create_fsm_diagram():
    dot = Digraph()

    # Define states
    dot.node('A', 'State A')
    dot.node('B', 'State B')
    dot.node('C', 'State C')

    # Define transitions
    dot.edge('A', 'B', label='Event 1')
    dot.edge('B', 'C', label='Event 2')
    dot.edge('C', 'A', label='Event 3')

    # Save the diagram to a file
    dot.render('fsm_diagram', format='png', cleanup=True)