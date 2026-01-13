import pandas as pd
from pathlib import Path
import json

def to_float(s:str) -> float:
    try:
        return float(s)
    except ValueError:
        return float(s.split(" ")[0].replace(",", ""))

def floats(s: pd.Series) -> list[float]:
    return [to_float(x) for x in s]

DATAFOLDER = Path(__file__).parent.parent / "data"
CASEFOLDER = DATAFOLDER / "cases"

with open(DATAFOLDER / "state_abbrevs.json") as f:
    ABBREVS = json.load(f)

def lookup_abbrev(state: str):
    for key, val in ABBREVS.items():
        if val == state:
            return key

def convert():
    df1 = pd.read_csv(CASEFOLDER / "state_level_cases.csv")
    df_state = pd.read_csv(CASEFOLDER / "2024_state_level_cases.csv")
    df_state["Year"] = ["2024" for _ in range(len(df_state))]

    df = pd.concat([df1[["Year", "Geography", "Cases", "Rate per 100000"]], df_state])
    geographies = df.Geography.unique()
    out = {}
    for geography in geographies:
        df3: pd.DataFrame = df[df.Geography==geography]
        df3 = df3.copy()
        df3.sort_values(by="Year", inplace=True, ignore_index=True)
        out[lookup_abbrev(geography)] = {"Year":floats(df3.Year), 
                          "Cases":floats(df3.Cases), 
                          "Rate per 100000":floats(df3["Rate per 100000"])}
    df4 = pd.read_csv(CASEFOLDER / "latent.csv")
    df4 = df4[df4.Grouping == "Total estimated number of persons with LTBI"]
    for i,row in df4.iterrows():
        state = row.Area.strip() 
        if state in ABBREVS:
            out[state]["latent_cases"] = row["Persons with LTBI (95%CI)"].split(" (")[0].strip()
            out[state]["latent_pct"] = row["LTBI % (95%CI)"].split(" (")[0].strip()
        else:
            print(state, ABBREVS)

    df_county = pd.read_csv(CASEFOLDER / "2023_county_level_cases.csv")
    df_county["State"] = [s.split(", ")[-1] for s in df_county.Geography]

    for i, row in df_county.iterrows():
        try:
            cases = int(row["Cases"])
        except ValueError:
            pass
        else:
            state = row["State"]
            if "counties" not in out[state]:
                out[state]["counties"] = {}
            out[state]["counties"][row["Geography"]] = cases

    with open(CASEFOLDER / "cases.json", "w") as f:
        json.dump(out, f)

if __name__=="__main__":
    convert()