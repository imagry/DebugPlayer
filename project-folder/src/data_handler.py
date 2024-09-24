# data_handler.py

from PySide6.QtWidgets import QFileDialog, QMessageBox, QApplication
import pandas as pd
import sys
import utils.analysis_manager.data_preparation as data_preparation
from utils.analysis_manager.config import DataFrameType, ClassObjType    
class DataHandler:
    def __init__(self, default_trip_path=None):
        self.time_data = []
        self.main_data = pd.DataFrame()
        self.secondary_data = {}
        self.temporal_data = {}
        self.df_list = {}
        self.ClassObjList={}
        if default_trip_path is not None:
            self.load_trip_data(default_trip_path)

    def load_data(self):
        """
        Loads trip data from a file and stores it in respective dataframes.
        """
        trip_path= QFileDialog.getExistingDirectory(None, "Select Data Directory")
        if trip_path:
           self.load_trip_data(self, trip_path)
        return False

    def get_time_data(self):
        return self.time_data

    def get_main_data(self):
        return self.main_data

    def get_secondary_data(self):
        return self.secondary_data

    def get_temporal_data(self):
        return self.temporal_data

    def get_signals(self):
        return list(self.temporal_data.columns)
    
    def load_trip_data(self, trip_path):
        """
        Refreshes the trip data based on the given path.
        """
        try:
            # Load car pose data
            try:    
                df_car_pose = data_preparation.prepare_car_pose_data(trip_path, interpolation=False) 
                self.df_list[DataFrameType.CAR_POSE] = df_car_pose
                # extract the time data from df_car_pose and store it in self.time_data
                self.time_data = df_car_pose['system_time_stamp'].values
            except:
                print("\033[91mCar Pose data not found\033[0m")            
            # Load steering data
            try:
                df_steering = data_preparation.prepare_steering_data(trip_path, interpolation=False) 
                self.df_list[DataFrameType.STEERING] = df_steering
            except: 
                print("\033[93mSteering data not found\033[0m")                        
            # Load path trajectory data
            try:
                PathObj = data_preparation.prepare_path_data(trip_path, interpolation=False) 
                self.ClassObjList[ClassObjType.PATH] = PathObj
            except:
                print("\033[91mPath Trajectory data not found\033[0m")                
            # Load Path Extraction data
            try:
                PathExtractionObj = data_preparation.prepare_path_extraction_data(trip_path, interpolation=False)
                self.ClassObjList[ClassObjType.PATH_EXTRACTION] = PathExtractionObj
            except:
                print("\033[93mPath Extraction data not found\033[0m")
            # load path adjustment data
            try:
                path_adjustment = data_preparation.prepare_path_extraction_data(trip_path, path_file_name="path_adjustment.csv\033[0m",
                                                                                interpolation=False)
                self.ClassObjList[ClassObjType.PATH_ADJUSTMENT] = path_adjustment
            except:
                print("\033[93mPath Adjustment data not found\033[0m")            
            
            QMessageBox.information(None, "Success", "Data loaded successfully!")
            return True
        except Exception as e:
                QMessageBox.critical(None, "Error", f"Failed to load data: {e}")
                        
    
