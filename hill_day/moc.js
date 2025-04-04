function prep_link(link, title){
    return "<a class=navbutton href=".concat(link, ">", title, "</a>")
}

function assign_span(id, link, title){
    $(id).append(prep_link(link, title))
    $(id).show()
}

function in_office(data, legislator){
    if (!legislator.hasOwnProperty("id")){
        return true
    }
    var bill_date
    if (data.hasOwnProperty("meta")){
        if (data.meta.hasOwnProperty("bill")){
            bill_date = new Date(data.meta.bill.introducedDate)
        }
        else{
            bill_date = new Date(data.meta.amendment.proposedDate)
        }
    }
    else if (data.summaries.summaries.length==0){
        bill_date = new Date(data.actions.actions[0].updateDate)
    }
    else{
        bill_date = new Date(data.summaries.summaries[0].updateDate)
    }
    var bill_type
    if (data.summaries.hasOwnProperty("request")){
        bill_type = data.summaries.request.billType
    }
    else{
        bill_type = data.meta.request.amendmentType
    }
    var terms = legislator.terms
    var start, end, bt0
    for (let i=terms.length-1; i>=0; i--){
        start = new Date(terms[i].start)
        end = new Date(terms[i].end)
        // console.log(bill_date, start, end, bill_type, terms[i].type, data.titles.titles[0].title)
        if (start<bill_date && end>bill_date){
            bt0 = bill_type.charAt(0)
            return ((terms[i].type=="rep" && bt0 == "h") || (terms[i].type=="sen" && bt0 == "s"))
        }
    }
}

function convert_type(bill_type){
    return {"hr":"house-bill", "hres":"house-resolution", "s":"senate-bill", "sres":"senate-resolution", "samdt":"senate-amendment"}[bill_type]
}

function year_section(data, legislator, good){
    if (!in_office(data, legislator)){
        return ""
    }
    h = ""
    var meta
    var billType
    var summary_text = ""
    if (data.summaries.hasOwnProperty("summaries")){
        var summaries = data.summaries.summaries
        if (summaries.length>0){
            summary_text = summaries[summaries.length-1].text
        }
    }
    if (data.meta.hasOwnProperty("amendment")){
        meta = data.meta.amendment
        billType = data.meta.request.amendmentType
        h = h.concat('<details class=not-clickable>')
    }
    else{
        meta = data.meta.bill
        billType = data.summaries.request.billType
        if (summary_text==""){
            h = h.concat('<details class=not-clickable>')
        }
        else{
            h = h.concat('<details>')
        }
    }
    h = h.concat("<summary>")
    var req = data.meta.request
    if (good){
        yes_icon = "&#x2705"
        no_icon = "&#x274c;"  
    }
    else{
        yes_icon = "&#x1F6A9;"
        no_icon = "&#x1F60C;"
    }
    neutral_icon = "&#x26AB;"
    if (legislator.hasOwnProperty("id")){
        const s = meta.sponsors
        var is_cosponsor = false
        for (let i=0; i<s.length; i++){
            if (s[i].bioguideId==legislator.id.bioguide){
                h = h.concat(yes_icon, " Sponsor")
                is_cosponsor = true
            }
        }
        if (!is_cosponsor){
            const cs = data.cosponsors.cosponsors
            for (let i=0; i<cs.length; i++){
                if (cs[i].bioguideId==legislator.id.bioguide){
                    is_cosponsor = true
                    if (cs[i].isOriginalCosponsor){
                        h = h.concat(yes_icon, " Original Cosponsor")
                    }
                    else{
                        h = h.concat(yes_icon, " Cosponsor")
                    }
                    h = h.concat(" as of ", cs[i].sponsorshipDate, "")
                }
            }
        }
        if (!is_cosponsor){
            h = h.concat(no_icon, " Not a cosponsor")
        }
        if (data.hasOwnProperty("rolls")){
            if (data.rolls.hasOwnProperty(legislator.id.bioguide)){
                var vote = data.rolls[legislator.id.bioguide]
                if (vote=="Yea"){
                    h = h.concat(", ", yes_icon, " Voted Yea")
                }
                else if (vote=="Nay"){
                    h = h.concat(", ", no_icon, " Voted Nay")
                }
                else{
                    h = h.concat(", ", neutral_icon," ", vote)
                }
            }
        }
        h = h.concat(": ")
    }
    if (billType.includes("amdt")){
        h = h.concat( "<a href=", "https://www.congress.gov/amendment/", req.congress, "/", convert_type(billType), "/", req.amendmentNumber, ">", meta.purpose, "</a> ", billType.toUpperCase().concat(".", req.amendmentNumber, ", Congress ", req.congress,", ", new Date(data.meta.amendment.proposedDate).toLocaleDateString(), "</summary>\n"))
    }
    else{
        h = h.concat( "<a href=", "https://www.congress.gov/bill/", req.congress, "/", convert_type(req.billType), "/", req.billNumber, ">", meta.title, "</a> ", req.billType.toUpperCase().concat(".", req.billNumber, ", Congress ", req.congress,", ", new Date(data.meta.bill.introducedDate).toLocaleDateString(), "</summary>\n"))
    }
    h = h.concat(summary_text)
    h = h.concat( "</details>")
    return h
}

function letter_section(data, legislator){
    if (!in_office(data, legislator)){
        console.log('not in office')
        return ""
    }
    var summary = data.summaries.summaries
    var titles = data.titles.titles
    h = ""
    h = h.concat('<details class=not-clickable><summary>')
    var req = data.summaries.request
    if (legislator.hasOwnProperty("id")){                
        const cs = data.cosponsors.cosponsors
        var is_cosponsor = false
        for (let i=0; i<cs.length; i++){
            if (cs[i].bioguideId==legislator.id.bioguide){
                is_cosponsor = true
                h = h.concat("&#x2705 Signed: ")
            }
        }
        if (!is_cosponsor){
            h = h.concat("&#x274c; Not signed: ")
        }
    }
    if (req.url!=""){
        h = h.concat( "<a href=", req.url, ">", titles[0].title, "</a> </summary></details>")
    }
    else{
        h = h.concat( titles[0].title, "</summary></details>")
    }
    
    return h
}

function capitalizeFirstLetter(val) {
    return String(val).charAt(0).toUpperCase() + String(val).slice(1);
}

function get_bills(legislator){
    var end_tb = ["118_hr_1776", "118_s_288", "117_hr_8654", "117_s_3386", "116_s_2438", "110_hr_1567"]
    var farmer = ["117_hres_1373", "118-hres_204", "118_sres_95"]
    var results = ['118_hres_1286', '117_hr_8057',  '116_hres_517', '116_hres_861', '115_hr_4022', '118_sres_684','117_s_1451','116_sres_511','116_s_1766', '116_sres_318',]
    var other = [ '118_s_4879', '118_s_5278', '118_s_4797', '118_hr_6705', '118_hr_10457', '118_hr_6424',  '117_s_962', '117_s_2586', '117_sres_137', '117_sres_569','117_hr_5857', '117_hr_391', '117_s_4662',  '116_s_1250', '116_s_834', '116_s_3829', '116_s_2698', '116_hr_4847', '116_hr_2401', '116_hr_3080', '116_hr_3460', '116_hr_826',   '116_sres_119',   '115_s_640', '115_sres_437', '114_s_289', '114_hr_2104', '113_s_2115', '113_sres_393', '113_hres_133', '111_sres_454', '111_hres_1155', '110_hr_1532', '110_s_1551',  '107_s_1115', '101_hr_4273']
    
    var bills = end_tb.concat(results, other, farmer)
    for (let i=0; i<bills.length; i++){
        $.getJSON("data/bills/".concat(bills[i], ".json"), function (data) {
        $('#'.concat(bills[i])).append(year_section(data, legislator, true))
        })
    }

    var bad = ["119_samdt_1266"]
    for (let i=0; i<bad.length; i++){
        $.getJSON("data/bills/".concat(bad[i], ".json"), function (data) {
        $('#'.concat(bad[i])).append(year_section(data, legislator, false))
        })
    }
}

function get_letters(legislator){
    var bills = [ "FY25FSTDCL", "FY25FSMGaNDCL", "FY25FSGFaPDCL", "FY25FHTDCl", "FY25FHMaGDCL", "FY24FSMGaNDCL", "FY24FSGFaPDCL", "FY24FHTDCl", "FY23FSMGaNDCL", "FY23FSGTDCL", "FY23FSGFaPDCL", "FY23FHTDCL", "FY22FSGTDCL", "FY22FHMGaNDCL", "FY22FHGTDCL", "FY22FHGFaPDCL", "FY21FSMGaNDCL", "FY21FSGTDCL", "FY21FSGFaPDCL", "FY21FHMGaNDCL", "FY21FHGTDCL", "FY21FHGFaPDCL", "FY20FSMGaNDCL", "FY20FSGTDCL", "FY20FSGFaPDCL", "FY20FHMGaNDCL", "FY20FHGTDCL", "FY20FHGFaPDCL", "FY19FSMGaNDCL", "FY19FSGTDCL", "FY19FSGFaPDCL", "FY19FHMGaNDCL", "FY19FHGTDCL", "FY19FHGFaPDCL", "FY23JLftUNHLMT"];
    for (let i=0; i<bills.length; i++){
        console.log(bills[i])
        $.getJSON("data/dcl/".concat(bills[i], ".json"), function (data) {
            ls = letter_section(data, legislator);
            console.log(ls)
            $('#'.concat(bills[i])).append(ls)
        })
    }
}

function get_terms(legislator){
    if (legislator.hasOwnProperty("leadership_roles")){
        var position = legislator.leadership_roles[legislator.leadership_roles.length - 1]
        if (new Date(position.end) > new Date()){
            $('#moc_title').append("<br>",position.title)
        }
    }
    var term
    var title = ""
    var new_title
    var start_year
    var end_year
    for (let i=0; i<legislator.terms.length; i++){
        term = legislator.terms[i]
        if (term.type=="rep"){
            new_title = "House ".concat(term.party, ", ", term.state, " District ", term.district)
        }
        else{
            new_title = "Senate ".concat(term.party,  ", ", term.state)
        }
        new_start_year = term.start.split("-")[0]
        new_end_year = term.end.split("-")[0]
        if(title==""){
            // first term
            title = new_title
            start_year = new_start_year
            end_year = new_end_year
        }
        else if (new_title!=title){
            // changed positions
            $('#terms').append("".concat(start_year, " - ", end_year, ": ", title, "<br>"))
            title = new_title
            start_year = new_start_year
            end_year = new_end_year
        }
        else if (new_start_year!=end_year){
            // gap between terms
            $('#terms').append("".concat(start_year, " - ", end_year, ", "))
            start_year = new_start_year
            end_year = new_end_year
        }
        else{
            end_year = new_end_year
        }
    }
    $('#terms').append("".concat(start_year, " - ", end_year, ": ", title, "<br>"))
}

function add_committee(member, comm){
    h = ""
    h = h.concat('<details>')
    h = h.concat("<summary>")
    if (member.hasOwnProperty("title")){
        h = h.concat("&#x1F3A9;<b>", member.title, "</b>: ")
    }
    h = h.concat(capitalizeFirstLetter(member.party), " member: ")
    h = h.concat("<a href=", comm.url, ">", comm.cname, "</a></summary>")
    if (comm.description!=null){
        h = h.concat(comm.description)
    }
    h = h.concat( "</details>")
    $('#comms').append(h)
}

function find_committee(committees, key){
    var top_thomas = key.replace(/[0-9]/g, "");
    var bot_thomas = key.replace(/\D/g,'');
    for (let i=0; i<committees.length; i++){
        if (committees[i].thomas_id==top_thomas){
            if (bot_thomas.length==0){
                return {"cname": committees[i].name, "url": committees[i].url, "description": committees[i].jurisdiction}
            }
            else{
                for (let j=0; j<committees[i].subcommittees.length; j++){
                    if (committees[i].subcommittees[j].thomas_id == bot_thomas){
                        return {"cname": committees[i].name.concat(" Subcommittee: ", committees[i].subcommittees[j].name), "url": committees[i].url, "description": committees[i].jurisdiction}
                    }
                }
            }
        }
    }
}

function relevant_committee(comm){
    return (comm.cname.includes("Health") || comm.cname.includes("Science") || comm.cname.includes("Research") || comm.cname.includes("State") || comm.cname.includes("Foreign") || comm.cname.includes("Drug") || comm.cname.includes("Pandemic"))
}

function get_committees(committees, committee_members, bioguide){
    var members
    var found = false
    for (const [key, members] of Object.entries(committee_members)){
        comm = find_committee(committees, key)
        if (relevant_committee(comm)){
            for (let j=0; j<members.length; j++){
                if (members[j].bioguide == bioguide){
                    add_committee(members[j], comm)
                    found = true
                }
            }
        }
    }
    if (!found){
        $('#comms').append("<ul><li>No relevant committees found.</li></ul>")
    }
}


function make_plot(case_line, rate_line){
        var dat = [case_line, rate_line]
        var lay = {"xaxis":{
                    "title":{"text":"Year"},
                    "zeroline":false,
                    "showline":false
                    },
                    "yaxis2": {
                    "title": {
                        "text": 'Rate per 100,000'
                    },
                    "overlaying": 'y',
                    "side": 'right',
                    "zeroline":false,
                    "rangemode":"tozero"
                    }, 
                    "yaxis":{
                    "title":{"text":"Cases"},
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
                    }
                }
        TESTER = document.getElementById('plot');
        Plotly.newPlot( TESTER, dat, lay, {responsive:true} );
    }

$(document).ready(function () { 
    // get charity name from the url params
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    const bioguide = decodeURI(urlParams.get('bioguide'))
    var legislator = {}
    var last_term
    var cases, abbrevs, grants
    const marker_size = 10
    const lw = 2
    const mode = "lines+markers"
    const colors = ["#BD4089",  "#143642", "#5DD39E","#809BCE"]
    $.when(
        $.getJSON("data/legislators-current.json", function (data) {
            for (let i=0; i<data.length; i++){
                if (data[i].id.bioguide==bioguide){
                    legislator = data[i]
                    last_term = legislator.terms[data[i].terms.length-1]
                }
            } 
            if (!legislator.hasOwnProperty("name")){
                $('#page_title').append("All bills")
            }
            else{
                $('#page_title').append(legislator.name.official_full)
                $('#page_title').append(" (".concat(last_term.party[0], " - ", last_term.state, ")"))
                if (last_term.type=="sen"){
                    $('#moc_title').append(capitalizeFirstLetter(last_term.state_rank).concat(" Senator"))
                }
                else if (last_term.type=="rep"){
                    $('#moc_title').append("Representative from District ".concat(last_term.district));
                    $('#119_samdt_1266').append("<ul><li>None found</li></ul>")
                }
                assign_span('#url', last_term.url, "Website")
                assign_span('#govtrack', "https://www.govtrack.us/congress/members/".concat(legislator.name.first, "_", legislator.name.last, "/", legislator.id.govtrack), "GovTrack")
                assign_span('#opensecrets', "https://www.opensecrets.org/members-of-congress/summary?cid=".concat(legislator.id.opensecrets, "&cycle=2022"), "OpenSecrets")
                assign_span("#congress", "https://www.congress.gov/member/".concat(legislator.name.first.toLowerCase(), "-", legislator.name.last.toLowerCase(), "/", legislator.id.bioguide), "Congress.gov")
                if (last_term.hasOwnProperty("contact_form")){
                    assign_span("#contact", last_term.contact_form, "Contact")
                }
                $('#phone').append(last_term.phone)
                $('#address').append(last_term.address)  
            };
             
        }),
        $.getJSON("data/cases/cases.json", function (data) {
            cases = data;
        }),
        $.getJSON("data/state_abbrevs.json", function (data) {
            abbrevs = data
        }),
        $.getJSON("data/grants.json", function (data){
            grants = data
        })
    ).then(function (){
        get_bills(legislator)
        get_letters(legislator)
        get_terms(legislator)
        var state = abbrevs[last_term.state]
        $('#case_header').append(" in ", state)
        var case_rates = cases[state]
        var years = case_rates.Year.length
        $('#case_count').append("In ".concat(case_rates.Year[years-1], ", there were <b>", case_rates.Cases[years-1], " active </b> cases, or <b>", case_rates["Rate per 100000"][years-1], " active </b> cases per 100,000 people."))
        $('#latent_count').append("".concat(state, " has <b>", case_rates.latent_cases, " latent</b> TB cases, or <b>", (case_rates.latent_pct*1000).toLocaleString(), " latent</b> TB cases per 100,000 people."))
        var case_line = {
                "x":case_rates.Year,
                "y":case_rates.Cases,
                "line":{"color":colors[1], "width":lw},
                "marker":{
                    "color":colors[1],
                    "symbol":"triangle-right-open",
                    "size":marker_size,
                    "line":{"width":lw}
                },
                "mode":mode,
                "name":"Cases"
            };
        var rate_line = {
                "x":case_rates.Year,
                "y":case_rates["Rate per 100000"],
                "line":{"color":colors[0], "width":lw},
                "marker":{
                    "color":colors[0],
                    "symbol":"square-open",
                    "size":marker_size,
                    "line":{"width":lw}
                },
                "yaxis":"y2",
                "mode":mode,
                "name":"Rate per 100,000"
            };
        make_plot(case_line, rate_line)
        var key
        if (last_term.type=="sen"){
            key = last_term.state
        }
        else{
            key = last_term.state.concat(last_term.district)
        }
        if (grants.hasOwnProperty(key)){
            $('#grants').append("<details class=not-clickable><summary>".concat(key," Fiscal Year 2024: ", grants[key], "</summary></details>"))
        }
        else{
            $('#grants').append("<ul><li>None found</li></ul>")
        }
    });

    var committee_members, committees
    $.when(
        $.getJSON("data/committees-current.json", function (data){
            committees = data
        }),
        $.getJSON("data/committee-membership-current.json", function(data){
            committee_members = data
        })
    ).then(function (){
        get_committees(committees, committee_members, bioguide)
    });

    $.getJSON("data/legislators-social-media.json", function (data){
        for (let i=0; i<data.length; i++){
            if (data[i].id.bioguide==bioguide){
                var social = data[i].social
                if (social.hasOwnProperty("twitter")){
                    assign_span('#twitter', "https://twitter.com/".concat(social.twitter), "Twitter")
                }
                if (social.hasOwnProperty("facebook")){
                    assign_span('#facebook', "https://facebook.com/".concat(social.facebook), "Facebook")
                }
                if (social.hasOwnProperty("instagram")){
                    assign_span('#instagram', "https://instagram.com/".concat(social.instagram), "Instagram")
                }
                if (social.hasOwnProperty("youtube")){
                    assign_span('#youtube', "https://youtube.com/@".concat(social.youtube), "YouTube")
                }
            }
        }
    }); 
}); 