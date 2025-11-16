"""Export videos, views, and features to the google spreadsheet."""

import pandas as pd
import json
from pathlib import Path

DATA_FOLDER = Path(__file__).parent.parent / "data"

def initialize_charity(key):
    d = {"Charity": key}
    d["2025_Videos"] = 0
    d["2025_Views"] = 0
    d["2025_Featured"] = ""
    return d

def fill_data():
    charities = {}

    cc = pd.read_csv(DATA_FOLDER / "charities.csv")
    for charity in cc["Charity"]:
        charities[charity] = initialize_charity(charity)

    # import features
    with open(DATA_FOLDER / "features.json") as f:
        features = json.load(f)
    for charity, val in features.items():
        if charity not in charities:
            print(charity)
        else:
            if "2025" in val:
                charities[charity]["2025_Featured"] = "x"

    # import view counts
    with open(DATA_FOLDER / "last_views.json") as f:
        views = json.load(f)
    for video in views:
        charity = video["Charity"]
        if charity not in charities:
            print(charity)
        else:
            charities[charity]["2025_Videos"] += 1
            charities[charity]["2025_Views"] += int(video["viewCount"])

    df = pd.DataFrame(charities.values())
    df.sort_values(by="Charity", inplace=True, key=lambda col: col.str.lower())
    df.reset_index(inplace=True, drop=True)
    df.to_csv(DATA_FOLDER / "google_temp.csv")

if __name__=="__main__":
    fill_data()

    

    