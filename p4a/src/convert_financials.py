import pandas as pd
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px
import json

def import_financials():
    df0 = pd.read_csv(Path(__file__).parent.parent / "data" / "financials.csv")
    df = df0[df0.legal==1]
    df = df[df.rs!='assets']

    li = []
    years = df.keys()[4:]
    for i,row in df.iterrows():
        for year in years:
            x = f"{year} {row['rs'].lower()}"
            if pd.isna(row[year]):
                if year==years[0]:
                    if row["Title"]=="P4A Grants":
                        val = -float(df0[df0.Title=="Grants"].iloc[0][year].replace(",","").replace("$",""))
                        x = f"{x} (Pledged)"
                        year = f"{year}*"
                    elif row["Title"]=="P4A Income":
                        val = float(df0[df0.Title=="P4A revenue"].iloc[0][year].replace(",","").replace("$",""))
                        x = f"{x} (Website)"
                        year = f"{year}*"
                    else:
                        val = 0
                else:
                    val = 0
            else:
                val = float(row[year].replace(",","").replace("$",""))
                if row["rs"].lower()=="spending":
                    val = -val
                year = f"{year}^"
            if val!=0:
                li.append({
                "legal":row["legal"], 
                "rs":row["rs"].lower(), 
                "category":row["Category"],
                "title":row["Title"], 
                "x":x,
                "year":year,
                "Amount":val})
    df2 = pd.DataFrame(li)
    df2.sort_values(by="x", inplace=True)
    df2.reset_index(inplace=True, drop=True)
    df2.to_csv(Path(__file__).parent.parent / "data" / "financials_converted.csv")

    li2 = []
    row = df0[df0.Title=="End of year net assets (22)"].iloc[0]
    for year in years:
        if not pd.isna(row[year]):
            li2.append({"year":f"{year}^", "Amount":float(row[year].replace(",","").replace("$",""))})
    df3 = pd.DataFrame(li2)
    df2.sort_values(by="year", inplace=True)
    df3.to_csv(Path(__file__).parent.parent / "data" / "assets.csv")

def generate_html():
    # Sample data
    df = pd.read_csv(Path(__file__).parent.parent / "data" / "financials_converted.csv")

    # Create a bar chart
    fig = px.bar(df, 
                 x='year', 
                 y='Amount', 
                 color='category',
                 text='title', 
                 barmode='group',
                 template="seaborn")
    fig.update_layout(barmode='relative',
                      xaxis=dict(
                            title=dict(text=""),
                            dtick=1
                        ),
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1
                        )
                    )
    fig.update_traces(textposition='inside',
                      hovertemplate = '%{x}<br>%{text}<br>$%{y:,}',
                      hoverinfo='text')
    fig.update_layout(uniformtext_minsize=10, uniformtext_mode='hide')
    aw = 2
    fig.add_annotation(x="2019^", y=2*10**6,
            text="December<br>P4A",
            showarrow=True,
            arrowhead=1, xanchor='left',
            axref='pixel', ax=30, ay=0, arrowwidth=aw)
    fig.add_annotation(x="2021^", y=2.5*10**6,
            text="February<br>P4A",
            showarrow=True,
            arrowhead=1, xanchor='right',
            axref='pixel', ax=-30, ay=0, arrowwidth=aw)
    fig.add_annotation(x="2020^", y=1*10**6,
            text="no P4A",
            showarrow=True,
            arrowhead=1, xanchor='center',
            axref='pixel', ax=0, ayref='pixel', ay=-30, arrowwidth=aw)
    fig.add_annotation(x="2013^", y=0.5*10**6,
            text="This<br>P4A...",
            showarrow=True,
            arrowhead=1, xanchor='center',
            axref='pixel', ax=0, ayref='pixel', ay=-30, arrowwidth=aw)
    fig.add_annotation(x="2014^", y=-1*10**6,
            text="...paid for<br>these grants",
            showarrow=True,
            arrowhead=1, xanchor='center',
            axref='pixel', ax=0, ayref='pixel', ay=30, arrowwidth=aw)
    fig.add_annotation(x="2022^", y=2.5*10**6,
            text="But<br>now<br>P4A...",
            showarrow=True,
            arrowhead=1, xanchor='center',
            axref='pixel', ax=0, ayref='pixel', ay=-30, arrowwidth=aw)
    fig.add_annotation(x="2022^", y=-2.5*10**6,
            text="...pays for<br>same year<br>grants",
            showarrow=True,
            arrowhead=1, xanchor='center',
            axref='pixel', ax=0, ayref='pixel', ay=30, arrowwidth=aw)
    df2 = pd.read_csv(Path(__file__).parent.parent / "data" / "assets.csv")
    fig.add_trace(go.Scatter(x=(df.year.unique()), y=df2.Amount, mode="lines+markers", line_color="black", name="Net assets"))
    
    fig_dict = json.loads(fig.to_json())
    fig_dict["total_raised"] = "{0:,}".format(int(round(df[df.Amount>0].Amount.sum(), 0)))
    total_grants = int(round(-df[df.title=="P4A Grants"].Amount.sum(), 0))
    fig_dict["total_grants"] = "{0:,}".format(total_grants)
    fig_dict["other_expenses"] = "{0:,}".format(int(round(-df[df.Amount<0].Amount.sum() - total_grants,0)))

    with open(Path(__file__).parent.parent / "data" / 'financials.json', 'w', encoding='utf-8') as f:
        json.dump(fig_dict, f, ensure_ascii=False, indent=4)

if __name__=="__main__":
    import_financials()
    generate_html()