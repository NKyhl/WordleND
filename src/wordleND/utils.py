import json

def load_config(config_file):
    with open(config_file) as json_file:
        config = json.load(json_file)
    return config