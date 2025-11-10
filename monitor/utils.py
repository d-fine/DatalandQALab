import os
import json
import datetime

output_dir = os.path.join(os.path.dirname(__file__), "output")
cet_timezone = datetime.timezone(datetime.timedelta(hours=1))


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


def store_output(data: str, file_name: str, format_as_json: bool = False) -> None:
    os.makedirs(output_dir, exist_ok=True)
    with open(f"{output_dir}/{file_name}-{datetime.datetime.now(tz=cet_timezone)}", "w", encoding="utf-8") as f:
        if format_as_json:
            json.dump(data, f, indent=4, ensure_ascii=False)
        else:
            f.write(data)
