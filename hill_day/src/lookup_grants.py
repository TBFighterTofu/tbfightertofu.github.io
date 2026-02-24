import requests
from pathlib import Path
import json

NIH_URL = "https://api.reporter.nih.gov/v2/projects/search"
DATAFOLDER = Path(__file__).parent.parent / "data"
GRANTS_FOLDER = Path(__file__).parent.parent / "data" / "grants"

def lookup_grants():
    payload = {
        "criteria": {
            "include_active_projects": True,
            "advanced_text_search": { "operator": "or", "search_field": "projecttitle,terms", "search_text": "tuberculosis" },
        },
        "include_fields": [
            "ProjectSerialNum",
            "Organization",
            "ProjectNum",
            "AgencyIcFundings",
            # "PrefTerms",
             "PhrText",
            "AwardAmount",
            "OpportunityNumber",
            "ProjectTitle",
            "CongDist",
        ],
        "sort_field":"project_start_date",
        "sort_order":"desc"
    }

    res = requests.post(NIH_URL, json = payload)
    if res.status_code == 200:
        results = res.json()["results"]
        return results
    else:
        res.raise_for_status()

def export_grants(grants):
    out = {}
    for row in grants:
        state =  row["organization"]["org_state"]
        if state not in out:
            out[state] = []
        out[state].append({
            "project_num": row["project_num"],
            "project_serial_num": row["project_serial_num"],
            "opportunity_number": row["opportunity_number"],
            "organization": row["organization"]["org_name"],
            "state": row["organization"]["org_state"],
            "award_amount": row["award_amount"],
            "cong_dist": row["cong_dist"],
            "project_title": row["project_title"],
            "public_health_relevance": row["phr_text"],
            "agencies": ", ".join([a["abbreviation"] for a in row["agency_ic_fundings"]])
        })
    with open(GRANTS_FOLDER / "tb_grants.json", "w") as f:
        json.dump(out, f, indent = 4)
    
    
if __name__=="__main__":
    results = lookup_grants()
    export_grants(results)
    # print(results)