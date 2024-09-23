import pandas as pd
import matplotlib.pyplot as plt

def cruise_control_analysis(df_cc):
    # Convert the timestamp to datetime
    df_cc['timestamp'] = pd.to_datetime(df_cc['timestamp'], unit='s')
    # df_cc['timestamp'] = df_cc['timestamp'] - df_cc['timestamp'][0]
    # Set the timestamp as the index
    df_cc.set_index('timestamp', inplace=True)

# Compute the derivative (rate of change) of steer_command
    df_cc['steer_command_rate'] = df_cc['steer_command'].diff() / df_cc.index.to_series().diff().dt.total_seconds()

    # Plot steer_command and its derivative over time in a separate figure
    # Plot both headings and their rates as functions of arc length
    fig,(ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(15, 10), sharex=True)
    ax1.plot(df_cc.index, df_cc['steer_command'],color='b', label='Steer Command')
    ax1.legend()
    ax1.set_title('Steer Command over Time ')
    ax1.set_ylabel('Steer Command [deg]')    
    
    ax2.plot(df_cc.index, df_cc['steer_command_rate'],color='r', label='Steer Command Rate')
    ax2.legend()
    ax2.set_title('Steer Command Rate over Time ')
    ax2.set_ylabel('Steer Command Rate [deg/s]')
    
    ax3.plot(df_cc.index, df_cc['current_speed'],color='g', label='Steer Command')
    ax3.legend()
    ax3.set_title('Speed over Time')
    ax3.set_ylabel('Speed (m/s)')
    
    ax3.set_xlabel('Time [s]')
    
    # plt.tight_layout()
    plt.show()