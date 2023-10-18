import json
import os


def read_json() -> dict:
    print("Reading JSON...")

    filename: str = "StorableSidebar.json"
    library_path: str = os.path.join(
        os.path.expanduser("~/Library/Application Support/Arc/"), filename
    )

    try:
        with open(filename, "r") as f:
            print(f"> Found {filename} in current directory.")
            data: dict = json.load(f)

    except FileNotFoundError:
        try:
            with open(library_path, "r") as f:
                print(f"> Found {filename} in Library directory.")
                data: dict = json.load(f)

        except FileNotFoundError:
            print(
                '> File not found. Look for the "StorableSidebar.json" '
                'file within the "~/Library/Application Support/Arc/" folder.'
            )

    return data
