import json

def get_schema(data, indent=0):
    spacing = '  ' * indent
    if isinstance(data, dict):
        for key, value in data.items():
            print(f"{spacing}{key}: {type(value).__name__}")
            get_schema(value, indent + 1)
    elif isinstance(data, list):
        print(f"{spacing}List[{len(data)} items]")
        if data:
            get_schema(data[0], indent + 1)
    else:
        print(f"{spacing}{type(data).__name__}")

# Load JSON file
with open('response.json', 'r') as file:
    json_data = json.load(file)

# Extract and print all values of 'priority' key
def get_priority_values(data, priorities=None):
    if priorities is None:
        priorities = []
    if isinstance(data, dict):
        for key, value in data.items():
            if key == 'priority':
                priorities.append(value)
            get_priority_values(value, priorities)
    elif isinstance(data, list):
        for item in data:
            get_priority_values(item, priorities)
    return priorities

priorities = get_priority_values(json_data)
print("Priority values:", priorities)
get_schema(json_data)