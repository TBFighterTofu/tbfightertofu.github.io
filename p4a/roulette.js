function get_url(video) {
    if (video.externalThumbnailUrl!=null){
        return video.externalThumbnailUrl
    } else {
        return video.oembed.oembed.thumbnail_url
    }
}

function find_p4a_link(id, all_videos) {
    var url
    for (let i=0; i<all_videos.length; i++){
        url = get_url(all_videos[i])
        if (url.includes(id)){
            return "https://www.projectforawesome.com/videos/".concat(all_videos[i].Slug)
        }
    }
}

function refresh_videos(vlists, all_videos, featured_videos){
    var k = Math.floor(Math.random() * vids_cutoff)
    var id, link
    const slist = ["views", "likes", "comments"]
    const tlist = ["low", "med", "hi"]
    for (let i=0; i<slist.length; i++){
        for (let j=0; j<tlist.length; j++){
            id = "#".concat(tlist[j], slist[i])
            link = find_p4a_link(vlists[id][k].id, all_videos)
            $(id).attr("href", link)
        }
    }

    var fk = Math.floor(Math.random() * featured_videos.length)
    id = "#featured"
    $(id).attr("href", "https://www.projectforawesome.com/videos/".concat(featured_videos[fk].Slug))

}

var num_vids, vids_cutoff, vlists, all_videos, featured_videos
const tt = ["view", "like", "comment"]

$.when(
    $.getJSON("data/submissions_2026.json", function (data) {
        all_videos = (data["data"]);
        featured_videos = all_videos.filter(x=>x.isFeatured);
    }),
    $.getJSON("data/last_views_2026.json", function (data) { 
        var videos = data
        num_vids = data.length
        vids_cutoff = Math.ceil(num_vids/3)
        var vl = {}
        var vc = {}
        vlists = {}
        for (let j=0; j<tt.length; j++){
            cname = tt[j].concat("Count")
            for (let i=0; i<videos.length; i++){
                videos[i][cname] = Number(videos[i][cname])
            }
            vl = videos.map(x=>x[cname]).toSorted((a,b)=>a-b)
            clow = vl[vids_cutoff]
            chigh = vl[num_vids - vids_cutoff]
            vlists["#low".concat(tt[j], "s")] = videos.filter(x=>x[cname]<=clow)
            vlists["#med".concat(tt[j], "s")] = videos.filter(x=>x[cname]>=clow && x[cname]<=chigh)
            vlists["#hi".concat(tt[j], "s")] = videos.filter(x=>x[cname]>=chigh)
        }
        
    })
).then(function () {
    refresh_videos(vlists, all_videos, featured_videos)
    var link = document.getElementsByClassName('navbutton');
    for (let i=0; i<link.length; i++){
        link[i].addEventListener('click', e => {
            refresh_videos(vlists, all_videos, featured_videos);
            console.log("click")
        });
    }
})