
import requests
from typing import Literal
import os
from pathlib import Path
import json

API_KEY = os.environ.get('GOV_TOKEN')

data_folder = Path(__file__).parent.parent / "data" / "bills"


def bill_data(congress: int, bill_type: Literal["hr", "s"], bill_number: int, subheader: str) -> dict:
    url = f"https://api.congress.gov/v3/bill/{congress}/{bill_type}/{bill_number}/{subheader}?api_key={API_KEY}&limit=250"
    g = requests.get(url)
    return g.json()

def bill_meta(congress: int, bill_type: Literal["hr", "s"], bill_number: int) -> dict:
    url = f"https://api.congress.gov/v3/bill/{congress}/{bill_type}/{bill_number}?api_key={API_KEY}"
    g = requests.get(url)
    return g.json()


def bill_info(congress: int, bill_type: Literal["hr", "s"], bill_number: int) -> dict:
    out = {}
    for s in ["actions", "cosponsors", "summaries", "titles"]:
        out[s] = bill_data(congress, bill_type, bill_number, s)
    out["meta"] = bill_meta(congress, bill_type, bill_number)
    with open(data_folder / f"{congress}_{bill_type}_{bill_number}.json", "w") as f:
        json.dump(out, f)
    return out

if __name__=="__main__":
    blist = [(118, 's', 288),
             (118, 's', 4879),
             (118, 's', 5278),
             (118, 's', 4797),
             (118, 'sres', 684), 
             (118, 'hr', 1776), 
             (118, 'hr', 2940),
             (118, 'hr', 6705),
             (118, 'hr', 10457),
             (118, 'hr', 6424),
             (118, 'hres', 1286),
             (117, 's', 3386), 
             (117, 's', 1451),
             (117, 's', 962),
             (117, 's', 2586),
             (117, 'sres', 137),
             (117, 'sres', 569),
             (117, 'hr', 8654), 
             (117, 'hr', 8057), 
             (117, 'hr', 5857), 
             (117, 'hr', 391),
             (117, 's', 4662),
             (116, 's', 2438), 
             (116, 's', 1766), 
             (116, 's', 1250),
             (116, 's', 834),
             (116, 's', 3829),
             (116, 's', 2698),
             (116, 'hr', 4847),
             (116, 'hr', 2401),
             (116, 'hr', 3080),
             (116, 'hr', 3460),
             (116, 'hr', 826),
             (116, 'sres', 511), 
             (116, 'sres', 318), 
             (116, 'sres', 119),
             (116, 'hres', 189), 
             (116, 'hres', 861), 
             (116, 'hres', 517),
             (115, 'hr', 4022),
             (115, 's', 640),
             (115, 'sres', 437),
             (114, 's', 289),
             (114, 'hr', 2104),
             (113, 's', 2115),
             (113, 'sres', 393),
             (113, 'hres', 133),
             (111, 'sres', 454),
             (111, 'hres', 1155),
             (110, 'hr', 4543),
             (110, 'hr', 1532),
             (110, 's', 1551),
             (110, 'hr', 1567),
             (107, 's', 1115),
             (101, 'hr', 4273),
             ]
    for b in blist:
        congress = b[0]
        bill_type = b[1]
        bill_number = b[2]
        fname = data_folder / f"{congress}_{bill_type}_{bill_number}.json"
        if not fname.exists():
            bill_info(congress, bill_type, bill_number)
