import json

def load_config(config_file):
    try:
        with open(config_file) as json_file:
            config = json.load(json_file)
        return config
    except FileNotFoundError as e:
        print(f"Error loading config: {e}")
        return {}
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return {}