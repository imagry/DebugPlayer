# data_converters.py
import pickle
import utils.data_loaders.misc_data_loader_pandas as misc_data_loader

### carpose data
def save_car_pose_as_pickle(file_path, output_path, car_pose_data = None):
    
    """
    Reads car pose data using misc_data_loader.load_trip_car_pose_data and saves it as a pickle file.

    :param file_path: Path to the input file to read car pose data from.
    :param output_path: Path to the output pickle file to save the car pose data.
    """ 
    # Read the car pose data 
    if car_pose_data is None:
        car_pose_data = misc_data_loader.load_trip_car_pose_data(file_path)

    # Save the data as a pickle file
    with open(output_path, 'wb') as f:
        pickle.dump(car_pose_data, f)

    print(f"Car pose data saved to {output_path}")


def load_car_pose_from_pickle(pickle_path):
	"""
	Loads car pose data from a pickle file.

	:param pickle_path: Path to the pickle file to load car pose data from.
	:return: The loaded car pose data.
	"""
	with open(pickle_path, 'rb') as f:
		car_pose_data = pickle.load(f)
	
	return car_pose_data

### Path data
def save_path_handler_data_as_pickle(file_path, output_path, path_handler_data = None):    
    """
    Reads data using path_handler_loader_pandas.load_path_handler_data and saves it as a pickle file.

    :param file_path: Path to the input file to read data from.
    :param output_path: Path to the output pickle file to save the data.
    """
    import utils.data_loaders.path_handler_loader_pandas as path_handler_loader_pandas

    # Read the data
    if path_handler_data is None:
        path_handler_data = path_handler_loader_pandas.read_path_handler_data(file_path)
    
    # Save the data as a pickle file
    with open(output_path, 'wb') as f:
        pickle.dump(path_handler_data, f)

    print(f"Path handler data saved to {output_path}")

def load_path_handler_data_from_pickle(pickle_path):
    """
    Loads data from a pickle file.

    :param pickle_path: Path to the pickle file to load data from.
    :return: The loaded data.
    """
    with open(pickle_path, 'rb') as f:
        path_handler_data = pickle.load(f)
    
    return path_handler_data