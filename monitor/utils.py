import os
import json


def load_config(config_path: str) -> dict:
    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("Config file not found. Please ensure monitor/config.json exists.")
        exit(1)
    except json.JSONDecodeError:
        print("Error decoding JSON from config file. Please check the file format.")
        exit(1)
