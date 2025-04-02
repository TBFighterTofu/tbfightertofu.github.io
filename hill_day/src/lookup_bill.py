
import requests
from typing import Literal
import os
from pathlib import Path
import json
from bs4 import BeautifulSoup
from xml.etree import ElementTree

API_KEY = os.environ.get('GOV_TOKEN')

data_folder = Path(__file__).parent.parent / "data" / "bills"
LEGFOLDER = Path(__file__).parent.parent / "data"
with open(LEGFOLDER / "legislators-current.json") as f:
    LEGISLATORS = json.load(f)
with open(LEGFOLDER / "legislators-historical.json") as f:
    LEGISLATORS_H = json.load(f)
    LEGISLATORS_H.reverse()


def strip_link(link: BeautifulSoup, d: dict):
    vote = link.get("aria-label").split("Voted ")[-1]
    id = link.get("href").split("?index=")[-1].replace("/Members/", "")
    d[id] = vote

def find_roll_calls(congress: int, bill_type: Literal["hr", "s"], bill_number: int) -> dict:
    file = Path(__file__).parent.parent/"data"/"roll_calls"/f"{congress}_{bill_type}_{bill_number}.html"
    if not file.exists():
        return {}
    else:
        with open(file) as f:
            text = f.read()
        soup = BeautifulSoup(text, 'html.parser')
        links = soup.find_all("a")
        d = {}
        for link in links:
            strip_link(link, d)
        return d
    
def find_bioguide(member: ElementTree) -> str:
    lis = member.find("lis_member_id").text
    for lgroup in [LEGISLATORS, LEGISLATORS_H]:
        for legislator in lgroup:
            if "lis" in legislator["id"]:
                if legislator["id"]["lis"] == lis:
                    return legislator["id"]["bioguide"]
    return "NOT FOUND"
    
def extract_rolls(out: dict) -> None:
    if "actions" not in out:
        return
    out["rolls"] = {}
    for action in out["actions"]["actions"]:
        if "recordedVotes" in action:
            url = action["recordedVotes"][0]["url"]
            response = requests.get(url)
            tree = ElementTree.fromstring(response.content)
            members = tree.find("members")
            for member in members:
                out["rolls"][find_bioguide(member)] = member.find("vote_cast").text

def ba(bill_type):
    if "amdt" in bill_type:
        return "amendment"
    else:
        return "bill"

def bill_data(congress: int, bill_type: Literal["hr", "s"], bill_number: int, subheader: str) -> dict:
    url = f"https://api.congress.gov/v3/{ba(bill_type)}/{congress}/{bill_type}/{bill_number}/{subheader}?api_key={API_KEY}&limit=250"
    g = requests.get(url)
    return g.json()

def bill_meta(congress: int, bill_type: Literal["hr", "s"], bill_number: int) -> dict:
    url = f"https://api.congress.gov/v3/{ba(bill_type)}/{congress}/{bill_type}/{bill_number}?api_key={API_KEY}"
    g = requests.get(url)
    return g.json()


def bill_info(congress: int, 
              bill_type: Literal["hr", "s", "samdt", "hres", "sres"], 
              bill_number: int) -> dict:
    out = {}
    for s in ["actions", "cosponsors", "summaries", "titles"]:
        out[s] = bill_data(congress, bill_type, bill_number, s)
    out["meta"] = bill_meta(congress, bill_type, bill_number)
    extract_rolls(out)
    if len(out["rolls"])==0:
        out["rolls"] = find_roll_calls(congress, bill_type, bill_number)    
    with open(data_folder / f"{congress}_{bill_type}_{bill_number}.json", "w") as f:
        json.dump(out, f)
    return out

if __name__=="__main__":
    blist = [# (119, 'samdt', 1266),
        
            #  (118, 's', 288),
            #  (118, 's', 4879),
            #  (118, 's', 5278),
            #  (118, 's', 4797),
            #  (118, 's', 4773),

            #  (118, 'sres', 743),
            #  (118, 'sres', 684), 
            #  (118, 'sres', 258),
            (118, 'sres', 95),

            #  (118, 'hr', 1776), 
            #  (118, 'hr', 2940),
            #  (118, 'hr', 6705),
            #  (118, 'hr', 10457),
            #  (118, 'hr', 6424),
            #  (118, 'hr', 9161),

            #  (118, 'hres', 1314),
            #  (118, 'hres', 1286),
            #  (118, 'hres', 526),
            (118, 'hres', 204),
             
            #  (117, 's', 4662),
            #  (117, 's', 4486),
            #  (117, 's', 2586),
            #  (117, 's', 3386), 
            #  (117, 's', 1451),
            #  (117, 's', 962),

            #  (117, 'sres', 137),
            #  (117, 'sres', 569),
            #  (117, 'sres', 283),
            #  (117, 'sres', 684),

            #  (117, 'hr', 8654), 
            #  (117, 'hr', 8057), 
            #  (117, 'hr', 7585),
            #  (117, 'hr', 5857), 
            #  (117, 'hr', 391),

            #  (117, 'hres', 490),
            #  (117, 'hres', 1195),
            (117, 'hres', 1373),

            #  (116, 's', 4819),
            #  (116, 's', 3829),
            #  (116, 's', 2698),
            #  (116, 's', 2438), 
            #  (116, 's', 1766), 
            #  (116, 's', 1250),
            #  (116, 's', 834),

            #  (116, 'sres', 511), 
            #  (116, 'sres', 318), 
            #  (116, 'sres', 119),
             
            #  (116, 'hr', 6637),
            #  (116, 'hr', 4847),
            #  (116, 'hr', 2401),
            #  (116, 'hr', 3080),
            #  (116, 'hr', 3460),
            #  (116, 'hr', 826),

            #  (116, 'hres', 189), 
            #  (116, 'hres', 861), 
            #  (116, 'hres', 517),
            #  (116, 'hres', 444),

            #  (115, 'hr', 4022),

            #  (115, 's', 640),

            #  (115, 'sres', 437),

            #  (114, 's', 289),

            #  (114, 'hr', 2104),

            #  (113, 's', 2115),

            #  (113, 'sres', 393),

            #  (113, 'hres', 133),

            #  (111, 'sres', 454),

            #  (111, 'hres', 1155),

            #  (110, 'hr', 4543),
            #  (110, 'hr', 1567),
            #  (110, 'hr', 1532),
             
            #  (110, 's', 1551),

            #  (107, 's', 1115),

            #  (101, 'hr', 4273),
             ]
    for b in blist:
        congress = b[0]
        bill_type = b[1]
        bill_number = b[2]
        fname = data_folder / f"{congress}_{bill_type}_{bill_number}.json"
        # if not fname.exists():
        bill_info(congress, bill_type, bill_number)
