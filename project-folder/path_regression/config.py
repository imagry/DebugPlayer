# config.py
import os
import sys
import numpy as np
import multiprocessing

# Add the parent directory to sys.path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)
    
class Config:
    def __init__(self):
        self.cpu_num = multiprocessing.cpu_count() 
        self.MAX_WORKERS = np.floor(self.cpu_num * 0.8)
        self.CACHE_DIR = os.path.join(os.path.dirname(parent_dir), "personal-folder", "cache")
        self.caching_mode_enabled = True
        self.trip_path = None 
        
    def set_trip_path(self, trip_path):
        self.trip_path = trip_path
        return self.trip_path
    
    def get_trip_path(self):
        return self.trip_path
    
    def get_cache_dir(self):    
        return self.CACHE_DIR
    
    def get_cpu_num(self):
        return self.cpu_num

    def get_max_workers(self):
        return self.MAX_WORKERS
    
    def is_caching_mode_enabled(self):
        return self.caching_mode_enabled
    
    def toggle_prog_mode(self):
        self.caching_mode_enabled = not self.caching_mode_enabled
        return self.caching_mode_enabled  
    
    def reset(self):
        self.trip_path = None
        self.caching_mode_enabled = True
        return self.trip_path, self.caching_mode_enabled
    
    def __str__(self):
        return f"Config: trip_path={self.trip_path}, CACHE_DIR={self.CACHE_DIR}, cpu_num={self.cpu_num}, MAX_WORKERS={self.MAX_WORKERS}, caching_mode_enabled={self.caching_mode_enabled}"
    
    def __repr__(self):
        return f"Config: trip_path={self.trip_path}, CACHE_DIR={self.CACHE_DIR}, cpu_num={self.cpu_num}, MAX_WORKERS={self.MAX_WORKERS}, caching_mode_enabled={self.caching_mode_enabled}"
    
    def __eq__(self, other):
        return self.trip_path == other.trip_path and self.CACHE_DIR == other.CACHE_DIR and self.cpu_num == other.cpu_num and self.MAX_WORKERS == other.MAX_WORKERS and self.caching_mode_enabled == other.caching_mode
    
    def __ne__(self, other):
        return self.trip_path != other.trip_path or self.CACHE_DIR != other.CACHE_DIR or self.cpu_num != other.cpu_num or self.MAX_WORKERS != other.MAX_WORKERS or self.caching_mode_enabled != other.caching_mode_enabled
    
    def __hash__(self):
        return hash((self.trip_path, self.CACHE_DIR, self.cpu_num, self.MAX_WORKERS, self.caching_mode_enabled))



# Test the Config class
if __name__ == "__main__":  
    
    # Create an instance of the Config class
    config = Config()

    # Set the trip path
    config.set_trip_path("trip_path")

    # Get the trip path
    trip_path = config.get_trip_path()
    print(trip_path)

    # Get the cache directory
    cache_dir = config.get_cache_dir()
    print(cache_dir)

    # Get the number of CPUs
    cpu_num = config.get_cpu_num()
    print(cpu_num)

    # Get the maximum number of workers
    max_workers = config.get_max_workers()
    print(max_workers)

    # Check if caching mode is enabled
    caching_mode = config.is_caching_mode_enabled()
    print(caching_mode)

    # Toggle the program mode
    prog_mode = config.toggle_prog_mode()
    print(prog_mode)

    # Reset the configuration
    reset_config = config.reset()

    # Print the configuration
    print(config)




      
        