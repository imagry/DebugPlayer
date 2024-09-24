# main_analysis_manager.py
import argparse

# %% Import libraries
import os
import sys

# Adjust the path to import init_utils
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.insert(0, parent_dir)

from init_utils import initialize_environment

# Initialize the environment
initialize_environment()


import data_preparation as dp 

def parse_arguments():
    # Create an argument parser
    parser = argparse.ArgumentParser(description="Main Analysis Manager")    
    # Add the --trip argument
    parser.add_argument('--trip', type=str, help='Path to the trip file')    
    # Parse the command-line arguments
    args = parser.parse_args()    
    # Check if the --trip flag is provided
    if args.trip:
        trip_dir = args.trip
        return
    else:
        raise ValueError("Please provide the path to the trip file using the --trip flag")
            

def main():
    '''Run the path regression analysis'''
    # Parse the command-line arguments
    trip_path = parse_arguments()
    
    # # Load the data
    # data = dp.load_data()
    # # Preprocess the data
    # data = dp.preprocess_data(data)
    # # Split the data
    # data = dp.split_data(data)
    # # Train the model
    # model = dp.train_model(data)
    # # Save the model
    # dp.save_model(model)
    # # Evaluate the model
    # dp.evaluate_model(model, data)
    # # Make predictions
    # dp.make_predictions(model, data)

if __name__ == '__main__':       
    main()    
    
    