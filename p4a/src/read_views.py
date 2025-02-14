import requests
import json
import time
import pandas as pd
from pathlib import Path
import os

data_folder = Path(__file__).parent.parent / "data"
video_file = data_folder / "videos.csv"
all_views_file = data_folder / "all_views.json"
views_json = data_folder / "views.json"
last_views_json = data_folder / "last_views.json"

def import_video_list():
    v = pd.read_csv(video_file)
    v = v[v.Year==2025]
    v.reset_index(inplace=True, drop=True)
    return v

def scrape_view_chunk(vid_df: pd.DataFrame, timestamp) -> list[dict]:
    out = []
    API_KEY = os.environ.get('YT_TOKEN')
    VIDEO_ID = ",".join([s.split("?v=")[1] for s in vid_df.url])
    PARTS = 'statistics'
    url = f'https://www.googleapis.com/youtube/v3/videos?part={PARTS}&id={VIDEO_ID}&key={API_KEY}'
    response = requests.get(url).json()
    with open('video_test_data.json', 'w', encoding='utf-8') as f:
        json.dump(response, f, ensure_ascii=False, indent=4)
    vids_data = response["items"]
    for i,o in enumerate(vids_data):
        oo = {}
        oo["Charity"] = vid_df.iloc[i].Charity
        oo["Timestamp"] = timestamp
        oo["id"] = o["id"]
        stats = o["statistics"]
        oo = {**oo, **stats}
        out.append(oo)
    return out

def add_view_summary(new_dfs: pd.DataFrame):
    with open(all_views_file, "r") as f:
        d = json.load(f)
    d.append({"Timestamp":int(time.time()),
              "viewCount":int(pd.to_numeric(new_dfs["viewCount"]).sum()),
              "likeCount":int(pd.to_numeric(new_dfs["likeCount"]).sum()),
              "favoriteCount":int(pd.to_numeric(new_dfs["favoriteCount"]).sum()),
              "commentCount":int(pd.to_numeric(new_dfs["commentCount"]).sum()),
              })
    with open(all_views_file, "w") as f:
        json.dump(d, f)
    print(time.time(), all_views_file)

def scrape_views():
    views_df = pd.read_json(views_json)
    vid_df = import_video_list()
    dfs = []
    i = 0
    timestamp = time.time()
    while i*50 < len(vid_df):
        df = scrape_view_chunk(vid_df[50*i:min(50*(i+1), len(vid_df)-1)], timestamp)
        dfs = dfs + df
        i+=1
    new_dfs = pd.DataFrame(dfs)
    views_df = pd.concat([views_df, new_dfs])
    views_df.reset_index(inplace=True, drop=True)
    views_df.to_json(views_json, orient="records")
    print(timestamp, views_json)
    new_dfs.to_json(last_views_json, orient="records")
    print(timestamp, last_views_json)
    add_view_summary(new_dfs)
    return views_df

if __name__=="__main__":
    try:
        scrape_views()
    except:
        pass
    from read_website import refresh_votes, refresh_features
    try:
        refresh_votes()
    except:
        pass
    try:
        refresh_features()
    except:
        pass

