import yaml
import pandas as pd
import json


def load_config(path):
    if path.endswith('.yaml') or path.endswith('.yml'):
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    elif path.endswith('.json'):
        with open(path, 'r') as f:
            return json.load(f)
    else:
        raise ValueError('Unsupported config file format')


def save_output_csv(data, path):
    pd.DataFrame(data).to_csv(path, index=False)


def save_output_excel(data, path):
    pd.DataFrame(data).to_excel(path, index=False)
