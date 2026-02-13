const ytlink = "https://www.youtube.com/watch?v="
const start_time0 = 1771002000
var votes, views, likes, comments
const marker_size = 10
const lw = 2
const mode = "lines+markers"
const colors = ["#BD4089",  "#143642", "#5DD39E","#809BCE"]
const dy = -225
var annot = []

function prep_link(link, title){
    return "<a class=navbutton href=".concat(link, ">", title, "</a>")
}

function assign_span(id, link, title){
    $(id).append(prep_link(link, title))
    $(id).show()
}

function parseISOString(s) {
  var b = s.split(/\D+/);
  return new Date(Date.UTC(b[0], --b[1], b[2], b[3], b[4], b[5], b[6])).getTime() / 1000;
}

function feature_annot(start_time) {
    var fcap
    const classes = "video_div featured_web"
    if (start_time > start_time0) {
        
        annot.push({
            x: (start_time - start_time0)/60/60,
            y: 0,
            xref: 'x',
            yref: 'y',
            text: 'Featured',
            showarrow: true,
            arrowcolor: "#BD4089",
            bgcolor:"white",
            arrowsize: 2,
            ax: 0,
            ay: dy
        })
    }
    var dt = (new Date(start_time * 1000)).toLocaleString()
    fcap = "<br>Featured on web at<br>".concat(dt)
    return {"fcap":fcap, "classes":classes}
}

function video_div(d, features_web, features_stream, features_2026){
    if (d["Voting link"]!=""){
        href = d["Voting link"]
    } else {
        href = d["url"]
    }
    const submission = features_2026.data.filter(x=>x.Title==d["Title"])
    var feature_time = null
    if (submission.length > 0) {
        feature_time = submission[0]["featuredAt"]
    } else {
        feature_time = null
    }
    var vid_id = d["url"].replace(ytlink, "")
    var classes, fcap, user
    if (features_stream.includes(vid_id)){
        classes = "video_div featured_stream"
        fcap = "Featured on stream"
    }
    else if (feature_time!=null){
        ret = feature_annot(parseISOString(feature_time))
        fcap = ret["fcap"]
        classes = ret["classes"]
    }
    else if (features_web.hasOwnProperty(vid_id)){
        ret = feature_annot(features_web[vid_id].start)
        fcap = ret["fcap"]
        classes = ret["classes"]
    }
    else{
        classes = "video_div"
        fcap = ""
    }
    console.log(fcap, classes)
    if (d["User"]!=null){
        user = d["User"]
    } else {
        user = ""
    }
    return '<a href='.concat(href, '><div class="', classes, '"><img class="thumbnail" src="https://i.ytimg.com/vi/', d['url'].replace(ytlink, ""), '/mqdefault.jpg">', "<br><b>", d["Title"], "</b><br>", user, fcap, "</div></a>" )
}

function year_section(year, d, features_web, features_stream, features_2026){
    h = ""
    h = h.concat('<div class="year_section">')
    h = h.concat("<h2 class='year_title'>", year)
    if (d["featured"]){
        h = h.concat("  *Featured*")
    }
    h = h.concat("</h2><br>")

    var vd
    
    for (const [url, di] of Object.entries(d["Videos"])){
        
        if (features_web.hasOwnProperty(year)){
            fw = features_web[String(year)]
        }
        else{
            fw = {}
        }
        vd = video_div(di, fw, features_stream, features_2026)
        h = h.concat(vd)
    }
    h = h.concat("</div>")
    
    return h
}

function make_plot(){
    var dat = [comments, likes, views]
    xlist = [-72, 0, 48, 120]
    llist = ["Voting start", "P4A start", "P4A end", "Voting end"]
    for (let i=0; i<xlist.length; i++){
        annot.push({"x": xlist[i], y: 0, xref: 'x', yref: 'y', text: llist[i], showarrow: true, arrowcolor: "black", bgcolor:"white", arrowsize: 2, ax: 0,ay: dy*(4-i)/4})
    }
    var lay = {"xaxis":{
                    "title":{"text":"Hour of P4A"},
                    "zeroline":false,
                    "showline":false,
                    "tickmode":'array',
                    "tickvals": [-72, -60, -48,-36, -24,-12, 0,12, 24,36, 48,60, 72, 84, 96, 108, 120]
                },
                "yaxis2": {
                    "title": {
                    "text": 'Likes, comments'
                    },
                    "overlaying": 'y',
                    "side": 'right',
                    "zeroline":false,
                    "rangemode":"tozero"
                    }, 
                "yaxis":{
                    "title":{"text":"Views"},
                    "showline":false,
                    "rangemode":"tozero"
                },
                "legend": {
                    "x": 0.5,
                    "xanchor": 'center',
                    "y": 1,
                    "yanchor":"bottom",
                    "orientation":"h",
                    "font":{"size":20}
                },
                annotations: annot
                }
    TESTER = document.getElementById('plot');
    Plotly.newPlot( TESTER, dat, lay, {responsive:true} );
}


$(document).ready(function () { 
    // get charity name from the url params
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    const charity = decodeURI(urlParams.get('charity'));

    if (charity=="Partners in Health" || charity=="Save the Children"){
        $('#guarantee').append("Guaranteed funding in 2026.")
    }

    $('#page_title').append(charity)

    // FETCHING DATA FROM JSON FILE 
    $.getJSON("data/charities.json", function (data) { 
        const summary = data[charity]

        const tags = summary.Tags.split(";").map(x=>"<div class=charitytag>".concat(x, "</div>")).join("")
        $('#tags').append(tags)
        $('#total_grants').append(summary["Total grants"])
        if(summary["Annual Revenue"]=="$0" || summary["Annual Revenue"]==null){
            $('#revenue').append("Not found")
        }
        else{
            $('#revenue').append(summary["Annual Revenue"])
        }
        $('#num_grants').append(String(summary["Number of grants"]).concat(" grant", summary["Number of grants"]!=1?"s":""))
        if (summary["Most recent grant"]!="" && summary["Most recent grant"]!=null){
            $('#last_grant').append(", most recently in ".concat(summary["Most recent grant"]))
        }
        $('#videos').append(String(summary["Videos this year"]).concat(" video", summary["Videos this year"]==1?"":"s"))
        $('#videos_all').append(String(summary["All Videos"]).concat(" video", summary["All Videos"]==1?"":"s"))
        if (summary["Last featured"]!="" && summary["Last featured"]!=null){
            $('#last_feature').append("Last featured in ".concat(summary["Last featured"]))
        }
        
        const ein = summary["EIN"]
        if (ein!="" && ein.includes("-")){
            cn = "https://www.charitynavigator.org/ein/".concat(ein) 
            pp = "https://projects.propublica.org/nonprofits/organizations/".concat(ein)
            cl = "https://www.guidestar.org/profile/".concat(ein)
            assign_span('#charity_navigator', cn, "Charity Navigator")
            assign_span('#propublica', pp, "ProPublica")
            assign_span('#guidestar', cl, 'Guidestar')
        }
        else if (ein.includes("UK") || ein.includes("England")){
            ur = "https://register-of-charities.charitycommission.gov.uk/en/charity-search/-/results/page/1/delta/20/keywords/".concat(ein.replace("UK", "").replace("England", "").replace(" ", ""))
            assign_span('#ukregister', ur, "UK Register")
        }
        // else{
        //     ce = encodeURI(charity)
        //     cn = "https://www.charitynavigator.org/search?q=".concat(ce)
        //     pp = "https://projects.propublica.org/nonprofits/search?q=".concat(ce)
        //     cl = "https://www.guidestar.org/search?q=".concat(ce)
        // }
        if (summary.Website!="" && summary.Website!=null){
            assign_span("#website", summary.Website, "Website")
        }
    }); 

    $.getJSON("data/grants.json", function (data) { 
        if (data.hasOwnProperty(charity)){
            const grants = data[charity]
            for (let i=0; i<grants.length; i++){
                $('#funding_years').append("<b>".concat(grants[i].Year, "</b>: $", grants[i].Grant, "<br>"))
            }
        }
    })

    var videoData, features_web, features_2026;

    $.when(
        $.getJSON("data/videos.json", function(data) {
            videoData = data;
        }),
        $.getJSON("data/feature_times.json", function(data) {
            features_web = data;
        }),
        $.getJSON("data/submissions_2026.json", function(data) {
            features_2026 = data;
        }),
        
    ).then(function() {
        var features_stream = []
        if (videoData.hasOwnProperty(charity)){
            const videos = videoData[charity]
            var years = Object.keys(videos)
            years.sort((a,b)=>b-a)
            for (let i=0; i<years.length; i++){
                year = years[i]
                $('#tester').append(year_section(year, videos[year], features_web, features_stream, features_2026))
            }
            if (years[0]=="2026"){
                assign_span("#vote", Object.keys(videos[2026]["Videos"])[0]["Voting link"], "Vote")
            }
        } else {
            console.log("videos not found")
        }            
    });

    $.when(
        $.getJSON("data/views_2026.json", function (data) {
        data = data.filter(x=>x.Charity==charity)
        for (let i=0; i<data.length; i++){
            data[i].Timestamp = Math.round((data[i].Timestamp / (data[i].Timestamp>10**10?1000:1) - start_time0)/15)*15/60/60
        }
        gb = Object.groupBy(data, x=>x.Timestamp)
        timestamps = Object.keys(gb)
        views = []
        likes = []
        comments = []
        for (let i=0; i<timestamps.length; i++){
            ts = timestamps[i]
            views.push(gb[ts].reduce((partialSum, a) => partialSum + Number(a.viewCount), 0))
            likes.push(gb[ts].reduce((partialSum, a) => partialSum + Number(a.likeCount), 0))
            comments.push(gb[ts].reduce((partialSum, a) => partialSum + Number(a.commentCount), 0))
        }
        var viewCount = views[views.length-1];
        var likeCount = likes[likes.length-1];
        var commentCount = comments[comments.length-1];
            views = {
            "x":timestamps,
            "y":views,
            "line":{
                "color":colors[1],
                "width":lw
            },
            "marker":{
                "color":colors[1],
                "symbol":"triangle-right-open",
                "size":marker_size,
                "line":{"width":lw}
            },
            "mode":mode,
            "name":"Views: ".concat(viewCount)
            };
            likes = {
            "x":timestamps,
            "y":likes,
            "line":{
                "color":colors[2],
                "width":lw
            },
            "marker":{
                "color":colors[2],
                "symbol":"star-open",
                "size":marker_size,
                "line":{"width":lw}
            },
            "mode":mode,
            "yaxis":"y2",
            "name":"Likes: ".concat(likeCount)
            };
            comments = {
            "x":timestamps,
            "y":comments,
            "line":{
                "color":colors[3],
                "width":lw
            },
            "marker":{
                "color":colors[3],
                "symbol":"square-open",
                "size":marker_size,
                "line":{"width":lw}
            },
            "mode":mode,
            "yaxis":"y2",
            "name":"Comments: ".concat(commentCount)
            };
        })
    ).then(function() {
        make_plot()           
    });

    
}); 