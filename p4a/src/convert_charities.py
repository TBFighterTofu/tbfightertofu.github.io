import pandas as pd
from pathlib import Path
import string
import difflib

def make_website_link(link:str) -> str:
    if (pd.isna(link) or link==""):
        return ""
    link = str(link).lower()
    if not link.startswith("http"):
        return "http://"+link
    else:
        return link
    
def import_videos(names: list[str]):
    f0 = pd.read_csv(Path(__file__).parent.parent / "data" / "videos.csv")
    current_year = f0.Year.max()
    d = dict([n, {"Videos this year":0, "Videos since 2024":0}] for n in names)
    for i,row in f0.iterrows():
        name = row["Charity"]
        if name not in d:
            print(i, name, row["year"], difflib.get_close_matches(name, names))
        else:
            if row["Year"]==current_year:
                d[name]["Videos this year"] += 1
            d[name]["Videos since 2024"] += 1
    return d

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
    names = []
    grants = []
    years.sort()
    for i,row in f0.iterrows():
        funding = 0
        num_grants = 0
        most_recent_year = ""
        names.append(row["Charity"].strip())
        cd = {"Charity": row["Charity"].strip(), "Website": make_website_link(row["Website"]), "Passthrough":row["Passthrough"], "EIN":row["EIN"], "Tags":row["Tags"]}
        for year in years:
            ftag = f"{year}/Featured"
            if ftag in row:
                if not pd.isna(row[ftag]):
                    cd["Last featured"] = year
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
        cd["Most recent grant"] = most_recent_year
        charities.append(cd)
    vd = import_videos(names)
    for charity in charities:
        charity["Videos this year"] = vd[charity["Charity"]]["Videos this year"]
        charity["Videos since 2024"] = vd[charity["Charity"]]["Videos since 2024"]
    charitydf = pd.DataFrame(charities)
    charitydf.sort_values(by=["Total grants", "Most recent grant"], ascending=False, ignore_index=True, inplace=True)

    charitydf.to_csv(Path(__file__).parent.parent / "data" / "charities_converted.csv")
    charitydf.to_html(Path(__file__).parent / "templates" / "plain_table.html", index=False, render_links=True, table_id="charitytable", classes=[ "table", "stripe"], columns=["Charity", "Website", "Tags", "Total grants", "Number of grants", "Most recent grant", "Videos this year", "Videos since 2024", "Last featured"], na_rep="", float_format='${:,.2f}'.format)
    pd.DataFrame(grants).to_csv(Path(__file__).parent.parent / "data" / "grants.csv")



if __name__=="__main__":
    import_charities()
