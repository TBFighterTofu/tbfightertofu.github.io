import requests
import pandas as pd
from pathlib import Path
import json
import numpy as np
from metapub import PubMedFetcher

ops = ["PAR-24-100",
"PAR-24-231",
"PAR-24-145",
"PAR-24-144",
"PAR-24-112",
"PAR-24-111",
"PAR-24-059",
"RFA-NS-24-019",
"PAR-24-075",
"PAR-24-076",
"RFA-OD-24-010",
"PAR-24-064",
"RFA-MH-25-171",
"RFA-MH-25-170",
"RFA-DA-24-041",
"RFA-DA-24-040",
"RFA-ES-24-005",
"PAR-23-297",
"PAR-23-296",
"PAR-23-255",
"RFA-DA-24-033",
"RFA-DA-24-032",
"RFA-MH-25-136",
"RFA-MH-25-130",
"RFA-MH-22-185",
"PAR-24-051",
"RFA-DA-24-034",
"RFA-DA-24-031",
"PAR-23-169",
"RFA-AI-23-023",
"PAR-22-198",
"PAR-22-131",
"PAR-22-199",
"PAR-22-243",
"PAR-22-210",
"PAR-22-242",
"PAR-23-144",
"RFA-DC-24-001",
"PAR-23-191",
"RFA-MD-24-003",
"PAR-23-190",
"RFA-MD-24-005",
"PAR-23-060",
"PAR-23-061",
"PAR-23-062",
"PAR-23-084",
"RFA-DA-24-066",
"RFA-DA-24-067",
"PAR-24-240",
"PAR-23-158",
"PAR-23-157",
"PAR-23-111",
"PAR-23-148",
"PAR-23-206", "PAR-24-041"]

data_folder = Path(__file__).parent.parent / "data"
GRANT_FILE = data_folder / "canceled_grants.csv"
PUB_FILE = data_folder / "publications.csv"

def search_ops(ops: list) -> list[dict]:
    out = []
    url = f"https://api.reporter.nih.gov/v2/projects/search"
    params = {
            "criteria": {
                "opportunity_numbers": ops
            },
            "include_fields": ["ApplId", "ActivityCode", "AgencyIcAdmin", "AwardType", "BudgetStart", "BudgetEnd", "CoreProjectNum", "OrganizationType", "OpportunityNumber", "ProjectNumber", "AgencyIcFundings", "FundingMechanism", "FiscalYear", "Organization", "CongDist", "PhrText", "ProgramOfficers", "ProjectTitle", "DirectCostAmt", "IndirectCostAmt", "AwardAmount", "IsActive", "ContactPiName", "ProjectDetailUrl"],
            "offset": 0,
            "limit": 500,
            "sort_field": "fiscal_year",
            "sort_order": "asc"
        }
    g = requests.post(url, json = params)
    try:
        grants = g.json()["results"]
    except:
        grants = []
    slist = ["appl_id", "fiscal_year", "project_title","project_detail_url", "organization.org_state","cong_dist", "organization.org_name", "project_num",  "is_active", "contact_pi_name", "agency_ic_admin.name", "opportunity_number", "core_project_num",  "agency_code", "funding_mechanism", "direct_cost_amt", "indirect_cost_amt"]
    for grant in grants:
        gg = {}
        gg["total_cost"] = grant["direct_cost_amt"] + grant["indirect_cost_amt"]
        for s in slist:
            sresult = grant.copy()
            sparts = s.split(".")
            for s in sparts:
                sresult = sresult.get(s, {})
            if not isinstance(sresult, dict):
                gg[s] = sresult
        out.append(gg)    
    return out

def pub_citation(pmid) -> dict:
    fetch = PubMedFetcher()
    article = fetch.article_by_pmid(pmid)
    return {"title": article.title, "journal": article.journal, "year": article.year, "doi": article.doi, "pmc": article.pmc, "grants": article.grants,  "authors": article.authors, "citation": article.citation}

def search_pubs(core_project_nums) -> list[dict]:
    out = []
    url = f"https://api.reporter.nih.gov/v2/publications/search"
    params = {
            "criteria": {
                "core_project_nums": core_project_nums
            },
            "offset": 0,
            "limit": 500,
            "sort_field": "appl_ids",
            "sort_order": "asc"
        }
    g = requests.post(url, json = params)
    try:
        pubs = g.json()["results"]
    except:
        pubs = []
    for pub in pubs:
        pub_c = pub_citation(pub["pmid"])
        citation = {**pub, **pub_c}
        out.append(citation)
    return out

def grants() -> list[dict]:
    out = []
    grants = None
    for i in range(int(np.ceil(len(ops) / 10))):
        grants = search_ops(ops[(i*10):min((i+1)*10, len(ops))])
        out = out + grants
    df = pd.DataFrame(out)
    df.to_csv(GRANT_FILE, index = False)
    return out

def pubs() -> list[dict]:
    canceled_grants = pd.read_csv(GRANT_FILE, index_col = None)
    pubs = search_pubs(list(canceled_grants.core_project_num.unique()))
    df = pd.DataFrame(pubs)
    df.to_csv(PUB_FILE, index = False)
    return pubs

if __name__ == "__main__":
    # grants()
    pubs()