import pandas as pd
from pathlib import Path
import json
import difflib
from urllib.parse import quote
import requests
from datetime import datetime

CURRENT_YEAR = datetime.now().year
VIDEOS_THIS_YEAR = f"Videos this year"

def make_website_link(link:str) -> str:
    if (pd.isna(link) or link==""):
        return ""
    link = str(link).lower()
    if not link.startswith("http"):
        link = "http://"+link
    else:
        return link
    
def import_videos(names: list[str]):
    f0 = pd.read_csv(Path(__file__).parent.parent / "data" / "videos.csv")
    f0["views"] = f0["views"].fillna(0)
    current_year = f0.Year.max()
    d = dict([n, {VIDEOS_THIS_YEAR:0, "All Videos":0}] for n in names)
    dl =  {}
    for i,row in f0.iterrows():
        name = row["Charity"]
        if name not in d:
            print(i, name, row["Year"], difflib.get_close_matches(name, names))
        else:
            if row["Year"]==current_year:
                d[name][VIDEOS_THIS_YEAR] += 1
            d[name]["All Videos"] += 1
            if name not in dl:
                dl[name] = {}
            year = int(row["Year"])
            if year not in dl[name]:
                dl[name][year] = {"Videos":{row["url"]:dict(row)}, "featured":False}
            else:
                dl[name][year]["Videos"][row["url"]] = dict(row)
    return d, dl

def combine_dicts(dl, features):
    for cname,years in features.items():
        if cname not in dl:
            dl[cname] = {}
        for year in years:
            yr = int(year)
            if yr not in dl[cname]:
                dl[cname][yr] = {"Videos":{}, "featured":True}
            else:
                dl[cname][yr]["featured"] = True
    return dl


def import_charities():
    f0 = pd.read_csv(Path(__file__).parent.parent / "data" / "charities.csv", header=[0])
    years = []
    for key in f0.keys():
        if "Pledged" in key:
            years.append(key.split(" ")[0])
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
        for s in ["Passthrough", "EIN", "Website", "Tags", "Annual Revenue"]:
            if pd.isna(row[s]):
                row[s] = ""
        cd = {"Charity": cname, "Website": row["Website"], "Passthrough":row["Passthrough"], "EIN":row["EIN"], "Tags":row["Tags"], "Annual Revenue":row["Annual Revenue"]}
        features[cname] = []
        for year in years:
            ftag = f"{year} Featured"
            if ftag in row:
                if not pd.isna(row[ftag]):
                    cd["Last featured"] = year
                    features[cname].append(year)
            if year==str(CURRENT_YEAR) or (year==str(CURRENT_YEAR-1) and datetime.now().month<6):
                col = f"{year} Pledged"
            else:
                col = f"{year} Form 990"
                if col not in row:
                    col = f"{year} Pledged"
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
        charities.append(cd)
        cdict[cname] = cd
    vd, dl = import_videos(names)
    dlo = combine_dicts(dl, features)
    with open(Path(__file__).parent.parent / "data" / "videos.json", "w") as f:
        json.dump(dlo, f)
    for charity in charities:
        charity["Videos this year"] = vd[charity["Charity"]]["Videos this year"]
        charity["All Videos"] = vd[charity["Charity"]]["All Videos"]
    charitydf = pd.DataFrame(charities)
    charitydf.sort_values(by=["Total grants", "Most recent grant"], ascending=False, ignore_index=True, inplace=True)

    with open(Path(__file__).parent.parent / "data" / "charities.json", "w") as f: 
        json.dump(cdict, f)
    with open(Path(__file__).parent.parent / "data" / "grants.json", "w") as f: 
        json.dump(gdict, f)    
    charitydf.to_csv(Path(__file__).parent.parent / "data" / "charities_converted.csv")
    charitydf["Charity"] = [local_link(x) for x in charitydf["Charity"]]
    charitydf["Website"] = [self_link(x) for x in charitydf["Website"]]   
    charitydf["Tags"] = [style_tags(x) for x in charitydf["Tags"]] 
    html = charitydf.to_html(index=False, render_links=False, table_id="charitytable", classes=[ "table", "stripe"], columns=["Charity", "Tags", "Annual Revenue", "Total grants", "Number of grants", "Most recent grant", VIDEOS_THIS_YEAR], na_rep="", float_format='${:,.2f}'.format, escape=False)
    with open(Path(__file__).parent / "templates" / "plain_table.html", "w", encoding="utf-8") as f:
        f.write(html)
    

def local_link(charity):
    link = "charity_profile.html?charity=" + quote(charity)
    return f"<a href={link} class=lilbutton>{charity}</a>"

def self_link(charity):
    if charity!="":
        return f"<a href={make_website_link(charity)}>Website</a>"
    else:
        return ""
    
def styled_tag(tag: str) -> str:
    return f"<span class=liltag>{tag}</span>"

def style_tags(tags: str) -> str:
    return "".join([styled_tag(tag) for tag in tags.split("; ")])

if __name__=="__main__":
    import_charities()
