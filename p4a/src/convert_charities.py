import pandas as pd
from pathlib import Path
import json
import difflib
from urllib.parse import quote
import requests

def make_website_link(link:str) -> str:
    if (pd.isna(link) or link==""):
        return ""
    link = str(link).lower()
    if not link.startswith("http"):
        link = "http://"+link
    else:
        return link
    
def lookup_category(code: str):
    if code=="" or code is None:
        return ""
    return {'A': 'Arts, Culture & Humanities', 'B': 'Education', 'C': 'Environment', 'D': 'Animal-Related', 'E': 'Health Care', 'F': 'Mental Health & Crisis Intervention', 'G': 'Voluntary Health Associations & Medical Disciplines', 'H': 'Medical Research', 'I': 'Crime & Legal-Related', 'J': 'Employment', 'K': 'Food, Agriculture & Nutrition', 'L': 'Housing & Shelter', 'M': 'Public Safety, Disaster Preparedness & Relief', 'N': 'Recreation & Sports', 'O': 'Youth Development', 'P': 'Human Services', 'Q': 'International, Foreign Affairs & National Security', 'Y': 'Mutual & Membership Benefit', 'R': 'Civil Rights, Social Action & Advocacy', 'S': 'Community Improvement & Capacity Building', 'T': 'Philanthropy, Voluntarism & Grantmaking Foundations', 'U': 'Science & Technology', 'V': 'Social Science', 'W': 'Public & Societal Benefit', 'X': 'Religion-Related', 'Z': 'Unknown'}[code[0]]

def propublica_data(ein: str):
    if ein=="" or ein is None:
        return {"category":"", "revenue":""}
    url = f"https://projects.propublica.org/nonprofits/api/v2/organizations/{ein}.json"
    g = requests.get(url)
    try:
        d = g.json()["organization"]
        return {"category":lookup_category(d["ntee_code"]), "revenue":d["revenue_amount"]}
    except:
        return {"category":"", "revenue":""}
    
def import_videos(names: list[str]):
    f0 = pd.read_csv(Path(__file__).parent.parent / "data" / "videos.csv")
    current_year = f0.Year.max()
    d = dict([n, {"Videos this year":0, "Videos since 2024":0}] for n in names)
    dl =  {}
    for i,row in f0.iterrows():
        name = row["Charity"]
        if name not in d:
            print(i, name, row["year"], difflib.get_close_matches(name, names))
        else:
            if row["Year"]==current_year:
                d[name]["Videos this year"] += 1
            d[name]["Videos since 2024"] += 1
            if name not in dl:
                dl[name] = {}
            year = int(row["Year"])
            if year not in dl[name]:
                dl[name][year] = {"Videos":[dict(row)], "featured":False}
            else:
                dl[name][year]["Videos"].append(dict(row))
    return d, dl

def combine_dicts(dl, features):
    for cname,years in features.items():
        if cname not in dl:
            dl[cname] = {}
        for year in years:
            if int(year) not in dl[cname]:
                dl[cname][int(year)] = {"Videos":[], "featured":True}
            else:
                dl[cname][int(year)]["featured"] = True
    return dl


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
    cdict: dict[dict] = {}
    gdict: dict[list] = {}
    features: dict[list] = {}
    years.sort()
    for i,row in f0.iterrows():
        funding = 0
        num_grants = 0
        most_recent_year = ""
        cname = row["Charity"].strip()
        names.append(cname)
        for s in ["Passthrough", "EIN", "Website", "Tags"]:
            if pd.isna(row[s]):
                row[s] = ""
        cd = {"Charity": cname, "Website": row["Website"], "Passthrough":row["Passthrough"], "EIN":row["EIN"], "Tags":row["Tags"]}
        features[cname] = []
        for year in years:
            ftag = f"{year}/Featured"
            if ftag in row:
                if not pd.isna(row[ftag]):
                    cd["Last featured"] = year
                    features[cname].append(year)
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
                newrow = {"Charity":cname, "Year":int(year), "Grant":"{0:,}".format(int(val))}
                grants.append(newrow)
                if cname in gdict:
                    gdict[cname].append(newrow)
                else:
                    gdict[cname] = [newrow]
                
                funding = funding + val
                num_grants = num_grants + 1
                most_recent_year = year
        cd["Total grants"] = "${0:,}".format(int(funding))
        cd["Number of grants"] = num_grants
        cd["Most recent grant"] = most_recent_year
        pp = propublica_data(row["EIN"])
        if pp["category"]!="":
            cd["Tags"] = cd["Tags"] + ";" + pp["category"]
        if pp["revenue"]!="" and pp["revenue"] is not None:
            cd["Annual revenue"] = "${0:,}".format(int(pp["revenue"]))
        else:
            cd["Annual revenue"] = ""
        charities.append(cd)
        cdict[cname] = cd
    vd, dl = import_videos(names)
    dlo = combine_dicts(dl, features)
    with open(Path(__file__).parent.parent / "data" / "videos.json", "w") as f:
        json.dump(dlo, f)
    for charity in charities:
        charity["Videos this year"] = vd[charity["Charity"]]["Videos this year"]
        charity["Videos since 2024"] = vd[charity["Charity"]]["Videos since 2024"]
    charitydf = pd.DataFrame(charities)
    charitydf.sort_values(by=["Total grants", "Most recent grant"], ascending=False, ignore_index=True, inplace=True)

    with open(Path(__file__).parent.parent / "data" / "charities.json", "w") as f: 
        json.dump(cdict, f)
    with open(Path(__file__).parent.parent / "data" / "grants.json", "w") as f: 
        json.dump(gdict, f)    
    charitydf["Charity"] = [local_link(x) for x in charitydf["Charity"]]
    charitydf["Website"] = [self_link(x) for x in charitydf["Website"]]    
    charitydf.to_html(Path(__file__).parent / "templates" / "plain_table.html", index=False, render_links=False, table_id="charitytable", classes=[ "table", "stripe"], columns=["Charity", "Website", "Tags", "Annual revenue", "Total grants", "Number of grants", "Most recent grant", "Videos this year", "Videos since 2024", "Last featured"], na_rep="", float_format='${:,.2f}'.format, escape=False)
    charitydf.to_csv(Path(__file__).parent.parent / "data" / "charities_converted.csv")

def local_link(charity):
    link = "charity_profile.html?charity=" + quote(charity)
    return f"<a href={link}>{charity}</a>"

def self_link(charity):
    if charity!="":
        return f"<a href={make_website_link(charity)}>Link</a>"
    else:
        return ""

if __name__=="__main__":
    import_charities()
