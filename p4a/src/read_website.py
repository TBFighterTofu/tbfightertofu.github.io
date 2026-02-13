import requests
import json
import time
import pandas as pd
from pathlib import Path
from datetime import datetime

CURRENT_YEAR = str(datetime.now().year)

data_folder = Path(__file__).parent.parent / "data"
vote_count_json = data_folder / "vote_count.json"
features_json = data_folder / "feature_times.json"
submissions_2026_json = data_folder / "submissions_2026.json"
videos_file = data_folder / "videos.json"
feature_list_file = data_folder / "features.json"

video_csv = data_folder / "videos.csv"
views_file = data_folder / "views.csv"


def import_vote_count() -> pd.DataFrame:
    f0 = pd.read_json(vote_count_json)
    return f0


def read_submissions():
    url = "https://api.projectforawesome.com/api/submissions?pageSize=400"
    g = requests.get(url)
    if g.status_code == 200:
        return g.json()
    else:
        return {}
    
def download_submissions():
    res = read_submissions()
    with open(submissions_2026_json, "w") as f:
        json.dump(res, f, indent = 4)



# --------- OUTDATED

def read_votes():
    url = "https://projectforawesome.com/data?req=stats"
    g = requests.get(url)
    try:
        d = g.json()
        d["timestamp"] = time.time()
        return d
    except:
        return {}
    
def refresh_votes():
    rv = read_votes()
    if "votes" in rv:
        rv["votes"] = float(rv["votes"])
        rv["total"] = float(rv["total"])
        rv["donations"] = float(rv["donations"])
        try:
            f0 = import_vote_count()
            f0 = pd.concat([f0, pd.DataFrame([rv])])
        except pd.errors.EmptyDataError:
            f0 = pd.DataFrame([rv])
        f0.reset_index(drop=True, inplace=True)
        f0.to_json(vote_count_json, orient="records")
        print(time.time(), vote_count_json)

def read_featured():
    url = "https://projectforawesome.com/featured"
    g = requests.get(url)
    try:
        url = g.url
        return {"timestamp":time.time(), "video":url}
    except:
        return {}

def import_features_2() -> dict:
    with open(features_json, "r") as f:
        d = json.load(f)
    return d

def export_features_2(d) -> dict:
    print(time.time(), features_json)
    with open(features_json, "w") as f:
        json.dump(d, f)

def export_feature_list(id: str):
    with open(feature_list_file, "r") as f:
        fd = json.load(f)
    vf = pd.read_csv(video_csv)
    yf = f"https://www.youtube.com/watch?v={id}"
    row = vf[vf.url==yf]
    if len(row)>0:
        charity = row.iloc[0]["Charity"]
        if charity not in fd:
            fd[charity] = [CURRENT_YEAR]
        if CURRENT_YEAR not in fd[charity]:
            fd[charity].append(CURRENT_YEAR)
    with open(feature_list_file, "w") as f:
        json.dump(fd, f)
    print(time.time(), feature_list_file)

def refresh_features():
    rv = read_featured()
    if "video" in rv:
        f1 = import_features_2()
        id = rv["video"].replace("https://projectforawesome.com/watch?v=", "")
        if CURRENT_YEAR not in f1:
            f1[CURRENT_YEAR] = {}
        if id in f1[CURRENT_YEAR]:
            f1[CURRENT_YEAR][id]["end"] = time.time()
        else:
            f1[CURRENT_YEAR][id] = {"start":time.time(), "end":time.time()}
            export_feature_list(id)
        export_features_2(f1)

if __name__=="__main__":
    download_submissions()
