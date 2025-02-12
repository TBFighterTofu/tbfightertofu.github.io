import pandas as pd
from pathlib import Path
import string

def make_website_link(link:str) -> str:
    if (pd.isna(link) or link==""):
        return ""
    link = str(link).lower()
    if not link.startswith("http"):
        return "http://"+link
    else:
        return link

def import_charities():
    table_html = open(Path(__file__).parent / "templates" / "plain_table.html", "r", encoding="utf-8").read()  # table content

    template_string = open(Path(__file__).parent / "templates" / "table.html", "r").read()  # table formatting
    t = string.Template(template_string)
    result = t.safe_substitute(table_content = table_html)
    with open(Path(__file__).parent.parent / "charity_table.html", "w", encoding="utf-8") as f:
        f.write(result)



if __name__=="__main__":
    import_charities()
