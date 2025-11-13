

function prep_link(link, title, state){
    return `<a class="navbutton legislatorbutton" state=${state} href=${link}>${title}</a>`
}

function make_row(legislator){
    var new_dict = {}
    let last_term = legislator.terms[legislator.terms.length-1]
    let official_full = legislator.name.official_full || legislator.name.first.concat(" ", legislator.name.last);
    new_dict.title = official_full.concat(" (", last_term.party[0], " - ", last_term.state)
    new_dict.sortval = last_term.state
    if (last_term.type=="rep"){
        new_dict.title = new_dict.title.concat(last_term.district)
        new_dict.sortval = new_dict.sortval.concat(String(last_term.district).padStart(2, '0'))
    }
    else{
        new_dict.sortval = new_dict.sortval.concat(last_term.state_rank)
    }
    new_dict.title = new_dict.title.concat(") ")
    new_dict.html = prep_link("moc.html?bioguide=".concat(legislator.id.bioguide), new_dict.title, last_term.state).concat("")
    new_dict.body = last_term.type
    return new_dict
}

function filter_states(group){
    let state = group.id;
    var elems = document.querySelectorAll(".legislatorbutton");
    [].forEach.call(elems, function(el) {
        let el_state = $(el).attr("state")
        if (el_state === state){
            $(el).show();
        } else {
            $(el).hide();
        }
    });
}

$(document).ready(function () { 
    let hexmap = new HexMap($("#map"));
    var elems = document.querySelectorAll(".hexstate");

    [].forEach.call(elems, function(el) {
        el.addEventListener("click", (event)=>{filter_states(el)})
    });

    $.getJSON("data/legislators-current.json", function (data) {
                var ll = data.map(x=>make_row(x))
                var sens = ll.filter(x=>x.body=="sen")
                var reps = ll.filter(x=>x.body=="rep")
                reps.sort((a, b) => a.sortval.localeCompare(b.sortval));
                sens.sort((a, b) => a.sortval.localeCompare(b.sortval));
                $('#senator_links').append(sens.map(x=>x.html).join(""))
                $('#house_links').append(reps.map(x=>x.html).join(""))
            });
})