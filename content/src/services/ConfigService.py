import json


def read_config_file(filepath):
    f = open(file=filepath, mode='r')
    return json.load(f)