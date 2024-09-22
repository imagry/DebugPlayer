import utils.analysis_manager.data_preparation as data_preparation
from utils.analysis_manager.config import DataFrameType, ClassObjType    

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
                self.time_data = df_car_pose.index
            except Exception:
                print("\033[91mCar Pose data not found\033[0m")            
            
            # Load steering data
            try:
                df_steering = data_preparation.prepare_steering_data(trip_path, interpolation=False) 
                self.df_list[DataFrameType.STEERING] = df_steering
            except Exception: 
                print("\033[93mSteering data not found\033[0m")                        
            
            # Load path trajectory data
            try:
                PathObj = data_preparation.prepare_path_data(trip_path, interpolation=False) 
                self.ClassObjList[ClassObjType.PATH] = PathObj
            except Exception:
                print("\033[91mPath Trajectory data not found\033[0m")                
            
            # Load Path Extraction data
            try:
                PathExtractionObj = data_preparation.prepare_path_data(trip_path, path_file_name="path_extyraction.csv", interpolation=False)
                self.ClassObjList[ClassObjType.PATH_EXTRACTION] = PathExtractionObj
            except Exception:
                print("\033[93mPath Extraction data not found\033[0m")
            
            # load path adjustment data
            try:
                path_adjustment = data_preparation.prepare_path_data(trip_path, path_file_name="path_adjustment.csv", interpolation=False)
                self.ClassObjList[ClassObjType.PATH_ADJUSTMENT] = path_adjustment
            except Exception:
                print("\033[93mPath Adjustment data not found\033[0m")            
            
            QMessageBox.information(None, "Success", "Data loaded successfully!")
            return True
        except Exception as e:
                QMessageBox.critical(None, "Error", f"Failed to load data: {e}")