import sys
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget
from PySide6.QtGui import QPixmap

# %%
import os
# Description: A utility function to read multiple log files to obtain vehicle state
import polars as pl
from datetime import datetime
from graphviz import Digraph


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
    # dot.render('fsm_diagram', format='png', cleanup=True)
    
class FSMViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('FSM Viewer')

        # Create a central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Set up the layout
        layout = QVBoxLayout(central_widget)

        # Create a label to display the FSM image
        fsm_label = QLabel()
        pixmap = QPixmap('fsm_diagram.png')
        fsm_label.setPixmap(pixmap)
        layout.addWidget(fsm_label)

    
# %%
# if __name__ == '__main__':
#     # Test the function
#     import os
#     logs_file_path =  os.path.abspath('li_conditions_2024-11-07T15_00_53.csv')
    
#     df_li_fsm = read_li_fsm_logs(logs_file_path)
#     if df_li_fsm is not None:
#         print(df_li_fsm.head())
#         print(df_li_fsm.schema)
        
    
#     create_fsm_diagram()    

    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    
    logs_file_path =  os.path.abspath('li_conditions_2024-11-07T15_00_53.csv')

    df_li_fsm = read_li_fsm_logs(logs_file_path)
    if df_li_fsm is not None:
        print(df_li_fsm.head())
        print(df_li_fsm.schema)
    

    create_fsm_diagram()


    viewer = FSMViewer()
    viewer.show()
    sys.exit(app.exec())
        