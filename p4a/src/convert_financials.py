import pandas as pd
from pathlib import Path

def import_financials():
    df0 = pd.read_csv(Path(__file__).parent.parent / "data" / "financials.csv")
    df = df0[df0.legal==1]
    df = df[df.rs!='assets']

    li = []
    years = df.keys()[4:]
    for i,row in df.iterrows():
        for year in years:
            x = f"{year} {row['rs'].lower()}"
            if pd.isna(row[year]):
                if year==years[0]:
                    if row["Title"]=="P4A Grants":
                        val = -float(df0[df0.Title=="Grants"].iloc[0][year].replace(",","").replace("$",""))
                        x = f"{x} (Pledged)"
                        year = f"{year}*"
                    elif row["Title"]=="P4A Income":
                        val = float(df0[df0.Title=="P4A revenue"].iloc[0][year].replace(",","").replace("$",""))
                        x = f"{x} (Website)"
                        year = f"{year}*"
                    else:
                        val = 0
                else:
                    val = 0
            else:
                val = float(row[year].replace(",","").replace("$",""))
                if row["rs"].lower()=="spending":
                    val = -val
                year = f"{year}^"
            if val!=0:
                li.append({
                "legal":row["legal"], 
                "rs":row["rs"].lower(), 
                "category":row["Category"],
                "title":row["Title"], 
                "x":x,
                "year":year,
                "Amount":val})
    df2 = pd.DataFrame(li)
    df2.sort_values(by="x", inplace=True)
    df2.reset_index(inplace=True, drop=True)
    df2.to_csv(Path(__file__).parent.parent / "data" / "financials_converted.csv")

    li2 = []
    row = df0[df0.Title=="End of year net assets (22)"].iloc[0]
    for year in years:
        if not pd.isna(row[year]):
            li2.append({"year":f"{year}^", "Amount":float(row[year].replace(",","").replace("$",""))})
    df3 = pd.DataFrame(li2)
    df2.sort_values(by="year", inplace=True)
    df3.to_csv(Path(__file__).parent.parent / "data" / "assets.csv")

if __name__=="__main__":
    import_financials()