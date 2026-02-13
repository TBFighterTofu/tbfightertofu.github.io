import requests
from bs4 import BeautifulSoup
import pandas as pd
from pathlib import Path
import difflib
import os

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

def load_p4a_website():

    with open(Path(__file__).parent / "charity_list_temp.txt") as f:
        charity_options = BeautifulSoup(f.read(), "html.parser")
    charities = charity_options.find_all("option")

    charity_table = import_charities()

    charity_list = list(charity_table.index)
    cleaned_charities = dict([[remove_common_words(s), s] for s in charity_list])

    existing = []
    conversions = {
        "Uplift Organization": "Uplift",
        "Aid and Friendship Association": "Associação Auxílio e Amizade (Aid & Friendship Association)",
        "Alzheimer's Research UK": "Alzheimer's Society",
        "Camp Lilac by GenderSphere": "Camp Lilac",
        "NephCure": "NephCure Kidney International"
    }
    new = []
    codes = {}

    for charity in charities:
        name: str = charity.get_text()
        name = conversions.get(name, name)
        code = charity.get("value")
        if code is not None and code!="":
            codes[code] = name
            if name not in charity_list:
                close_matches = difflib.get_close_matches(remove_common_words(name), cleaned_charities.keys(), n=1, cutoff=0.7)
                if len(close_matches)>0:
                    conversions[name] = cleaned_charities[close_matches[0]]
                else:
                    new.append(name)
            else:
                existing.append(name)
    

    # print("New: ", new)
    # print("Old: ", existing)
    # print("Conversions: ", conversions) 

    with open(Path(__file__).parent / "video_list_temp.txt", encoding = "utf-8") as f:
        video_list = BeautifulSoup(f.read(), "html.parser")
    videos = video_list.find_all("div", class_ = "col")

    video_d = []
    new_charities = {}

    
    for video in videos:
        img_span = video.find("img")
        vid_code = img_span.get("src")
        href = "https://www.youtube.com/watch?v=" + vid_code.split("/")[-2]
        p4a_href = "https://projectforawesome.com" + video.find("a").get("href")
        text_divs = video.find_all("div", class_="text-truncate")
        charity_name = text_divs[0].get_text()
        charity_name = conversions.get(charity_name, charity_name)
        title = text_divs[1].get_text()
        video_d.append({"Year":2026, "Charity":charity_name, "Voting link": p4a_href, "Title":title, "url":href})

        meta = find_charity_info(href)
        print(charity_name)
        if charity_name in charity_list:
            charity_table.loc[charity_name, "2026 Videos"] = charity_table.loc[charity_name, "2026 Videos"] + 1
        else:
            if charity_name in new_charities:
                new_charities[charity_name]["Tags"] = join_tags(new_charities[charity_name]["Tags"], meta["categories"])
                new_charities[charity_name]["2026 Videos"] = new_charities[charity_name]["2026 Videos"] + 1
            else:
                new_charities[charity_name] = ({"Charity": charity_name, "All time funding (990)":0, "All time pledged":0, "Website":meta["link"], "Tags":meta["categories"], "2026 Videos": 1})

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