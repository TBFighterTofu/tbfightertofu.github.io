import requests
from bs4 import BeautifulSoup
import pandas as pd
from pathlib import Path
import difflib
import os
from read_website import read_submissions

DATA_FOLDER = Path(__file__).parent.parent / "data"

def import_charities():
    f0 = pd.read_csv(
       DATA_FOLDER  / "charities.csv", index_col = 0
    )
    return f0

def remove_common_words(s: str) -> str:
    s = s.replace("Project", "")
    s = s.replace("Foundation", "")
    s = s.replace(", Inc.", "")
    s = s.replace("Initiative", "")
    return s

def find_charity_link(youtube_url: str) -> str | None:
    API_KEY = os.environ.get('YT_TOKEN')
    VIDEO_ID = youtube_url.split("?v=")[1]
    PARTS = 'snippet'
    url = f'https://www.googleapis.com/youtube/v3/videos?part={PARTS}&id={VIDEO_ID}&key={API_KEY}'
    snippet = requests.get(url).json()
    if snippet is None or "error" in snippet:
        return None
    items = snippet["items"]
    if len(items) == 0:
        return None
    desc = items[0].get("snippet", {}).get("description", "")
    desc = desc.replace("\n", " ")
    for word in desc.split(" "):
        if word.startswith("http") or word.startswith("www.") or word.endswith(".org") or word.endswith(".com"):
            if "projectforawesome.com" not in word:
                return word
    return None

def find_charity_categories(soup: BeautifulSoup) -> str:
    a_list = soup.find_all(class_ = "filter-pill")
    return "; ".join([aa.get_text().lower().capitalize() for aa in a_list])

def find_charity_info(url: str) -> dict:
    return {"link": find_charity_link(url), "categories": ""}

def join_tags(old_tags, new_tags) -> str:
    if old_tags is None:
        return new_tags
    if new_tags is None:
        return old_tags
    return "; ".join(list(set([s.strip() for s in old_tags.split(";") + new_tags.split(";")])))

def coalesce_website(old_website, new_website):
    if old_website is not None and isinstance(old_website, str) and len(old_website)>1:
        return old_website
    return new_website

def extract_charity(row) -> str:
    if row is None:
        return ""
    charity_dict = row.get("charity")
    if charity_dict is None:
        return ""
    return charity_dict.get("Title", "")

def load_p4a_website():

    videos = read_submissions()["data"]

    new_charity_names = list(set([extract_charity(row) for row in videos]))

    charity_table = import_charities()
    charity_list = list(charity_table.index)
    cleaned_charities = dict([[remove_common_words(s), s] for s in charity_list])

    existing = []
    conversions = {
        "Uplift Organization": "Uplift",
        "Aid and Friendship Association": "Associação Auxílio e Amizade (Aid & Friendship Association)",
        "Alzheimer's Research UK": "Alzheimer's Society",
        "Camp Lilac by GenderSphere": "Camp Lilac",
        "NephCure": "NephCure Kidney International",
        "APOPO": "APOPO Herorats",
        "Yoga and Sports for Refugees": "Yoga and Sport with Refugees",
        "Doctors Without Borders (MSF)": "Doctors Without Borders"
    }
    new = []

    for charity in new_charity_names:
        name = conversions.get(charity, charity)
        if name not in charity_list:
            close_matches = difflib.get_close_matches(
                remove_common_words(name),
                cleaned_charities.keys(),
                n=1, cutoff=0.7
            )
            if len(close_matches)>0:
                conversions[name] = cleaned_charities[close_matches[0]]
            else:
                new.append(name)
        else:
            existing.append(name)


    # print("New: ", new)
    # print("Old: ", existing)
    # print("Conversions: ", conversions) 

    video_d = []
    new_charities = {}

    
    for video in videos:
        if video["Phase"] == "Approved":
            thumbnail = video["externalThumbnailUrl"]
            if thumbnail is None:
                thumbnail = video["oembed"]["oembed"]["thumbnail_url"]
            code = thumbnail.split("/")[-2]
            slug = video["Slug"]

            youtube_url = f"https://www.youtube.com/watch?v={code}"
            p4a_href = f"https://projectforawesome.com/{slug}"
            charity_name = video["charity"]["Title"]
            charity_name = conversions.get(charity_name, charity_name)
            title = video["Title"]

            video_d.append({"Year":2026, "Charity":charity_name, "Voting link": p4a_href, "Title":title, "url":youtube_url})

            print(charity_name)
            if charity_name in charity_list:
                charity_table.loc[charity_name, "2026 Videos"] = charity_table.loc[charity_name, "2026 Videos"] + 1
            else:
                categories = "; ".join([row["name"] for row in video["categories"]])
                if charity_name in new_charities:
                    new_charities[charity_name]["Tags"] = join_tags(new_charities[charity_name]["Tags"], categories)
                    new_charities[charity_name]["2026 Videos"] = new_charities[charity_name]["2026 Videos"] + 1
                else:
                    charity_link = find_charity_link(youtube_url)
                    new_charities[charity_name] = ({"Charity": charity_name, "All time funding (990)":0, "All time pledged":0, "Website":charity_link, "Tags":categories, "2026 Videos": 1})

    new_charity_table = pd.DataFrame(list(new_charities.values()))
    new_charity_table.set_index("Charity", inplace = True, drop = True)
    new_charity_table.to_csv(DATA_FOLDER / "new_charities.csv")
    pd.concat([charity_table, new_charity_table]).to_csv(DATA_FOLDER / "charities_updated.csv")
    
    pre_videos = pd.read_csv(DATA_FOLDER / "videos.csv")
    new_videos = pd.DataFrame(video_d)
    new_videos.to_csv(DATA_FOLDER / "new_videos.csv")
    pd.concat([pre_videos, new_videos]).to_csv(DATA_FOLDER / "videos_updated.csv")



if __name__=="__main__":
    load_p4a_website()