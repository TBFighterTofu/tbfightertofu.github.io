import pandas as pd
from pathlib import Path
import string

def make_website_link(link:str) -> str:
    if (pd.isna(link) or link==""):
        return ""
    link = str(link).lower()
    if not link.startswith("http"):
        return "http://"+link
    else:
        return link

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
    years.sort()
    for i,row in f0.iterrows():
        funding = 0
        num_grants = 0
        most_recent_year = ""
        cd = {"Charity": row["Charity"], "Website": make_website_link(row["Website"]), "Passthrough":row["Passthrough"], "EIN":row["EIN"], "Tags":row["Tags"]}
        for year in years:
            if year==years[-1]:
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
                most_recent_year = year
        cd["Total grants"] = funding
        cd["Number of grants"] = num_grants
        cd["Most recent year"] = most_recent_year
        charities.append(cd)
    charitydf = pd.DataFrame(charities)
    charitydf.sort_values(by=["Total grants", "Most recent year"], ascending=False, ignore_index=True, inplace=True)
    charitydf.to_csv(Path(__file__).parent.parent / "data" / "charities_converted.csv")
    charitydf.to_html(Path(__file__).parent / "templates" / "plain_table.html", index=False, render_links=True, table_id="charitytable", classes=[ "table", "stripe"], columns=["Charity", "Website", "Tags", "Total grants", "Number of grants", "Most recent year"], na_rep="", float_format='${:,.2f}'.format)
    pd.DataFrame(grants).to_csv(Path(__file__).parent.parent / "data" / "grants.csv")



if __name__=="__main__":
    import_charities()
