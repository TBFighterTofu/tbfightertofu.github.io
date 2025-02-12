import requests
import json
import time
import pandas as pd
from pathlib import Path

data_folder = Path(__file__).parent.parent / "data"
vote_count_file = data_folder / "vote_count.csv"
features_file = data_folder / "features_2025.csv"

video_file = data_folder / "videos.csv"
views_file = data_folder / "views.csv"

def import_vote_count() -> pd.DataFrame:
    f0 = pd.read_csv(vote_count_file)
    return f0

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
        try:
            f0 = import_vote_count()
            f0 = pd.concat([f0, pd.DataFrame([rv])])
        except pd.errors.EmptyDataError:
            f0 = pd.DataFrame([rv])
        f0.to_csv(vote_count_file, index=False)
        print(time.time(), vote_count_file)

def read_featured():
    url = "https://projectforawesome.com/featured"
    g = requests.get(url)
    try:
        url = g.url
        return {"timestamp":time.time(), "video":url}
    except:
        return {}

def import_features() -> pd.DataFrame:
    f0 = pd.read_csv(features_file)
    return f0

    
def refresh_features():
    rv = read_featured()
    if "video" in rv:
        f0 = import_features()
        if f0.iloc[-1]["video"]!=rv["video"]:
            f0 = pd.concat([f0, pd.DataFrame([rv])])
            f0.to_csv(features_file, index=False)
            print(time.time(), features_file)

if __name__=="__main__":
    while True:
        try:
            refresh_votes()
        except:
            pass
        try:
            refresh_features()
        except:
            pass
        time.sleep(60*5)
