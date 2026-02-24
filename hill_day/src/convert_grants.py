import pandas as pd
from pathlib import Path
import json
from datetime import datetime

DATAFOLDER = Path(__file__).parent.parent / "data"
GRANTS_FOLDER = Path(__file__).parent.parent / "data" / "grants"
CURRENT_YEAR = datetime.now().year

with open(DATAFOLDER / "state_abbrevs.json") as f:
    ABBREVS = json.load(f)

def lookup_abbrev(state: str):
    for key, val in ABBREVS.items():
        if val == state:
            return key

def key(row):
    if pd.isna(row.State) or row.State=="":
        return None
    if row.District == "At-Large":
        return f"{row.State}0"
    if row.District == "Total":
        return row.State
    elif row.District == "" or row.District is None:
        return None
    else:
        return f"{row.State}{row.District}"

def convert_grants():
    out = {}
    df = pd.read_csv(GRANTS_FOLDER / "NIAID grants.csv")
    state = ""
    for i, row in df.iterrows():
        if isinstance(row["District"], str) and "Summary for" in row["District"]:
            state = row["District"].replace("Summary for ", "").replace(" by Congressional District", "")
            state = lookup_abbrev(state)
        elif isinstance(row["District"], str) and row["District"] == "Congressional District":
            pass
        elif pd.isna(row["Year"]):
            pass
        else:
            if row["District"] == "At-Large":
                cd = 0
            elif row["District"] == "Total":
                cd = ""
            elif pd.isna(row["District"]):
                cd = ""
            else:
                cd = row["District"]
            full_district = f"{state}{cd}"
            if full_district not in out:
                out[full_district] = {}
                for year in range(2017, CURRENT_YEAR):
                    out[full_district][year] = {"Awards": 0, "Funding": 0}

            out[full_district][int(row["Year"])] = {
                "Awards": int(row["Awards"]),
                "Funding": int(row["Funding"].replace("$", "").replace(",",""))
            }

    with open(GRANTS_FOLDER / "grants.json", "w") as f:
        json.dump(out, f, indent = 4)
            
if __name__=="__main__":
    convert_grants()
