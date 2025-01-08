import pandas as pd
from pathlib import Path

def import_charities():
    f0 = pd.read_csv(Path(__file__).parent.parent / "data" / "charities.csv", header=[0,1,2])
    columns = []
    years = []
    year = ""
    for key in f0.keys():
        if "Unnamed" not in key[0] and len(key[0])==4 and key[0][0]=="2":
            year = key[0]
            years.append(year)
        if "Unnamed" in key[1]:
            columns.append(key[0])
        else:
            columns.append(year+"/"+key[1])
    f0.columns = columns
    charities = []
    grants = []
    for i,row in f0.iterrows():
        funding = 0
        num_grants = 0
        cd = {"Charity": row["Charity"], "Website": row["Website"], "Passthrough":row["Passthrough"], "EIN":row["EIN"], "Tags":row["Tags"]}
        for year in years:
            if year==years[0]:
                col = f"{year}/Pledged"
            else:
                col = f"{year}/Form 990"
                if col not in row:
                    col = f"{year}/Pledged"
            val = row[col]
            if not pd.isna(val):
                if isinstance(val, str):
                    val = float(val.replace(",","").replace("$",""))
                grants.append({"Charity":row["Charity"], "Year":year, "Grant":val})
                funding = funding + val
                num_grants = num_grants + 1
        cd["Total grants"] = funding
        cd["Number of grants"] = num_grants
        charities.append(cd)
    charitydf = pd.DataFrame(charities)
    charitydf.to_csv(Path(__file__).parent.parent / "data" / "charities_converted.csv")
    charitydf.to_html(Path(__file__).parent / "templates" / "table.html", index=False, render_links=True, classes="charitytable", na_rep="", float_format='${:,.2f}'.format)
    pd.DataFrame(grants).to_csv(Path(__file__).parent.parent / "data" / "grants.csv")



if __name__=="__main__":
    import_charities()
