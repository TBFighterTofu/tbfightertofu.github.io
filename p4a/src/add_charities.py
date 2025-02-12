import requests
from bs4 import BeautifulSoup
import pandas as pd
from pathlib import Path
import difflib
import re

def import_charities():
    f0 = pd.read_csv(Path(__file__).parent.parent / "data" / "charities.csv", header=[0,1,2])
    return f0

def remove_common_words(s: str) -> str:
    s = s.replace("Project", "")
    s = s.replace("Foundation", "")
    s = s.replace(", Inc.", "")
    s = s.replace("Initiative", "")
    return s

def find_charity_link(soup: BeautifulSoup) -> str:
    desc = soup.find(class_ = "video-desc")
    a_list = desc.find_all("a")
    for a in a_list:
        if "projectforawesome.com" not in a.get("href"):
            return a.get("href")
    return None

def find_charity_categories(soup: BeautifulSoup) -> str:
    cats = soup.find(class_ = "watch-category")
    a_list = cats.find_all("a")
    return "; ".join([aa.get_text().lower().capitalize() for aa in a_list])

def find_charity_info(url: str) -> str:
    response = requests.get(url.replace("https://www.youtube.com", "https://projectforawesome.com")).text
    soup = BeautifulSoup(response, "html.parser")
    return {"link": find_charity_link(soup), "categories": find_charity_categories(soup)}

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
    videos = []
    html_content = ""
    i = 1
    while "No videos found!" not in html_content and i<40:
        response = requests.get(f'https://projectforawesome.com/?mode=recent&page={i}')
        html_content = response.text
        
        # with open(Path(__file__).parent.parent / "data" / "p4a_source.html") as f:
        #     html_content = f.read()
        soup = BeautifulSoup(html_content, 'html.parser')
        if i==1:
            charity_options = soup.find(id="charity-form")
            charities = charity_options.find_all("option")
        videos = videos + soup.find_all(class_="video-block")
        i+=1

    charity_table = import_charities()

    charity_list = list(charity_table.Charity["Unnamed: 0_level_1"]["Year total"])
    cleaned_charities = dict([[remove_common_words(s), s] for s in charity_list])


    existing = []
    conversions = {}
    new = []
    codes = {}

    for charity in charities:
        name = charity.get_text()
        code = charity.get("value")
        if code is not None:
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

    video_d = []
    new_charities = {}

    
    for video in videos:
        link_span = video.find("a")
        href = "https://www.youtube.com" + link_span.get("href")
        title = link_span.find_all(class_ = "video-title")[0].get_text()
        user = video.find_all(class_ = "video-username")[0].get_text()
        charity_span = video.find_all(class_="video-charity")[0]
        charity_code = charity_span.get("href").replace("/?charity=", "")
        if charity_code not in codes:
            codes[charity_code] = charity_span.get_text()
            new.append(charity_span.get_text())
        charity_name = codes[charity_code]
        charity_name = conversions.get(charity_name, charity_name)
        video_d.append({"Year":2025, "Charity":charity_name, "User":user, "Title":title, "url":href})

        meta = find_charity_info(href)

        if charity_name in new:
            if charity_name in new_charities:
                new_charities[charity_name]["Tags"] = join_tags(new_charities[charity_name]["Tags"], meta["categories"])
                new_charities[charity_name]["Website"] = coalesce_website(new_charities[charity_name]["Website"], meta["link"])
            else:
                new_charities[charity_name] = ({"Charity": charity_name, "All time funding":0, "All time pledged":0, "Website":meta["link"], "Tags":meta["categories"]})
        else:
            charity_table[charity_table.Charity["Unnamed: 0_level_1"]["Year total"]==charity_name]["2025"]["Videos"]["0"] = charity_table[charity_table.Charity["Unnamed: 0_level_1"]["Year total"]==charity_name]["2025"]["Videos"]["0"] + 1

            charity_table[charity_table.Charity["Unnamed: 0_level_1"]["Year total"]==charity_name]["Website"]["Unnamed: 3_level_1"]["Unnamed: 3_level_2"] = coalesce_website(charity_table[charity_table.Charity["Unnamed: 0_level_1"]["Year total"]==charity_name].iloc[0]["Website"]["Unnamed: 3_level_1"]["Unnamed: 3_level_2"], meta["link"])


    pd.DataFrame(list(new_charities.values())).to_csv(Path(__file__).parent.parent / "data" / "new_charities.csv")
    pd.DataFrame(video_d).to_csv(Path(__file__).parent.parent / "data" / "new_videos.csv")
    pd.DataFrame(charity_table).to_csv(Path(__file__).parent.parent / "data" / "charities_updated.csv")



if __name__=="__main__":
    load_p4a_website()