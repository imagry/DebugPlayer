import pandas as pd
import matplotlib.pyplot as plt

def merge_time_series(df1, df2, interpolation=False):
    
    # If one of the DataFrames is empty, return the other
    if df1 is None:
        return df2
    if df2 is None:
        return df1  
    
    # Check if the index is already set to 'timestamp'
    if df1.index.name != 'timestamp' and 'timestamp' not in df1.columns:
        raise ValueError('Timestamp column not found in df1')
    if df2.index.name != 'timestamp' and 'timestamp' not in df2.columns:
        raise ValueError('Timestamp column not found in df2')
    
    # TODO: fix this check and make sure it is really necessary
    # if df1['timestamp'].dtype != df2['timestamp'].dtype and df1['timestamp'].dtype != 'datetime64[ns]' and df2['timestamp'].dtype != 'datetime64[ns]':
    #     raise ValueError('Timestamp column data type mismatch')
    
    
    # Set the index if not already set
    if df1.index.name != 'timestamp':        
        df1 = df1.drop_duplicates(subset='timestamp')        
        df1.set_index('timestamp', inplace=True)
    if df2.index.name != 'timestamp':
        df2 = df2.drop_duplicates(subset='timestamp')
        df2.set_index('timestamp', inplace=True)

    # Create a common time index
    common_index = df1.index.union(df2.index)
    
    # Reindex the DataFrames
    df1_reindexed = df1.reindex(common_index)
    df2_reindexed = df2.reindex(common_index)
    
    # Interpolate if required
    if interpolation:
        df1_reindexed = df1_reindexed.interpolate(method='time')
        df2_reindexed = df2_reindexed.interpolate(method='time')

    # Merge the DataFrames
    df_combined = pd.concat([df1_reindexed, df2_reindexed], axis=1)

    return df_combined

if __name__ == "__main__":
    # Sample DataFrames
    df1 = pd.DataFrame({
        'timestamp': pd.date_range(start='2023-01-01', periods=100, freq='T'),
        'value1': range(100)
    })
    df2 = pd.DataFrame({
        'timestamp': pd.date_range(start='2023-01-01 00:05', periods=80, freq='2T'),
        'value2': range(80)
    })

    # # Set the timestamp as the index
    # df1['timestamp'] = pd.to_datetime(df1['timestamp'], unit='s')    
    # df1.set_index('timestamp', inplace=True)
    # df2['timestamp'] = pd.to_datetime(df2['timestamp'], unit='s')
    # df2.set_index('timestamp', inplace=True)
    
    
        
    # Merge without interpolation
    df_combined_no_interpolation = merge_time_series(df1.copy(), df2.copy(), interpolation=False)

    # Merge with interpolation
    df_combined_with_interpolation = merge_time_series(df1.copy(), df2.copy(), interpolation=True)

    # Plot the data
    plt.figure(figsize=(10, 6))
    plt.plot(df_combined_no_interpolation.index, df_combined_no_interpolation['value1'], label='Series 1 (No Interpolation)')
    plt.plot(df_combined_no_interpolation.index, df_combined_no_interpolation['value2'], label='Series 2 (No Interpolation)')
    plt.plot(df_combined_with_interpolation.index, df_combined_with_interpolation['value1'], label='Series 1 (With Interpolation)', linestyle='dashed')
    plt.plot(df_combined_with_interpolation.index, df_combined_with_interpolation['value2'], label='Series 2 (With Interpolation)', linestyle='dashed')
    plt.xlabel('Time')
    plt.ylabel('Values')
    plt.title('Aligned Time Series Data')
    plt.legend()
    plt.show()