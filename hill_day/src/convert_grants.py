import pandas as pd
from pathlib import Path
import json

DATA_FOLDER = Path(__file__).parent.parent / "data"

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
    df = pd.read_csv(DATA_FOLDER / "grants.csv")
    df = df[df.Year==2024]
    for i, row in df.iterrows():
        row_key = key(row)
        if row_key is not None:
            out[row_key] = row["Funding"]
    with open(DATA_FOLDER / "grants.json", "w") as f:
        json.dump(out,f)
            
if __name__=="__main__":
    convert_grants()
