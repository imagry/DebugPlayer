import argparse

def parse_arguments():
    # Create an argument parser
    parser = argparse.ArgumentParser(description="Main Analysis Manager")    
    # Add the --trip argument
    parser.add_argument('--trip1', type=str, help='Path to the first trip file')
    parser.add_argument('--trip2', type=str, default=None, help='Path to the second trip file')
    # Parse the command-line arguments
    args = parser.parse_args()    
    # Check if the --trip flag is provided
    if args.trip1 and args.trip2:
        return args.trip1, args.trip2
    elif args.trip1:
        return args.trip1
    else:
        raise ValueError("Please provide the paths to both trip files using the --trip1 and --trip2 flags")
