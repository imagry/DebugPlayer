# new_data_loader.py

import polars as pl
from datetime import datetime


def read_path_data(path):
    """
    Reads path data from a CSV file and returns a DataFrame.
    """
    df = pl.read_csv(path)
    
    # scan columns and sort them into : columns that has path_x in col to path_x_columns, and path_y_columns to columns with path_y in col, and fixed_columns to all other columns
    
    
    # Extract fixed columns - no 'path_x_' or 'path_y_' prefix
    fixed_columns = [col for col in df.columns if not 'path_x' in col and not 'path_y' in col]
    
    
    return df



# Add a test for the read_path_data function here
if __name__ == "__main__":
    
    
    # Assuming df is your Polars DataFrame
    df = pl.DataFrame({
        'path_x1': [1, 2, 3],
        'path_y1': [4, 5, 6],
        'other': [7, 8, 9]
    })

    # Use lazy API to filter columns
    lazy_df = df.lazy()

    path_x_columns = lazy_df.select(pl.col('*path_x*')).collect()
    path_y_columns = lazy_df.select(pl.col('*path_y*')).collect()
    fixed_columns = lazy_df.select(pl.exclude(['*path_x*', '*path_y*'])).collect()

    # Convert back to lists of column names if needed
    path_x_columns = path_x_columns.columns
    path_y_columns = path_y_columns.columns
    fixed_columns = fixed_columns.columns


    path = 'ExampleData/path_trajectory.csv'
    df = read_path_data(path)
    # print(df)