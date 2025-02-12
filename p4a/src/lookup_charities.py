import pandas as pd
from pathlib import Path
import json
import difflib
from urllib.parse import quote
import requests
    
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
  
def join_tags(old_tags, new_tags) -> str:
    if old_tags is None:
        old_tags = ""
    if new_tags is None:
        new_tags = ""
    l = list(set([s.strip().lower() for s in old_tags.split(";") + new_tags.split(";")]))
    l = list(filter(lambda x: len(x)>0, l))
    l.sort()
    l = [li.capitalize() for li in l]
    return "; ".join(l)


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
        pp = propublica_data(row["EIN"])
        cd["Tags"] = join_tags(cd["Tags"], pp["category"])
        if pp["revenue"]!="" and pp["revenue"] is not None:
            cd["Annual revenue"] = "${0:,}".format(int(pp["revenue"]))
        else:
            cd["Annual revenue"] = ""
        charities.append(cd)
        cdict[cname] = cd
    charitydf = pd.DataFrame(charities)
    charitydf.sort_values(by="Charity", inplace=True, ignore_index=True)
    charitydf.to_csv(Path(__file__).parent.parent / "data" / "charity_revenue.csv")


if __name__=="__main__":
    import_charities()
