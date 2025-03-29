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

def convert():
    df1 = pd.read_csv(Path(__file__).parent.parent / "data/AtlasPlusTableData.csv")
    df2 = pd.read_csv(Path(__file__).parent.parent / "data/2024_cases.csv")
    df2["Year"] = ["2024" for _ in range(len(df2))]
    df = pd.concat([df1[["Year", "Geography", "Cases", "Rate per 100000"]], df2])
    geographies = df.Geography.unique()
    out = {}
    for geography in geographies:
        df3: pd.DataFrame = df[df.Geography==geography]
        df3 = df3.copy()
        df3.sort_values(by="Year", inplace=True, ignore_index=True)
        out[geography] = {"Year":floats(df3.Year), 
                          "Cases":floats(df3.Cases), 
                          "Rate per 100000":floats(df3["Rate per 100000"])}
    with open(Path(__file__).parent.parent / "data" / "cases" / f"cases.json", "w") as f:
        json.dump(out, f)

if __name__=="__main__":
    convert()