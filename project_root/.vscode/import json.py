import json
import re

def read_launch_json(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Remove comments using a regular expression
    # content = re.sub(r'\/\/.*', '', content)
    
    # Parse the JSON content
    return json.loads(content)

# Example usage
file_path = '/home/thamam/dev/DebugPlayer/personal-folder/.vscode/launch.json'
try:
    launch_config = read_launch_json(file_path)
    # Print the parsed data
    print(launch_config)
except Exception as e:
    print(f"Error reading or parsing the file: {e}")