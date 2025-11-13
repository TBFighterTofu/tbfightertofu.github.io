
class HexMap{
    constructor(parent){
        this.state = "";
        this.initializeMap(parent);
    }

    initializeMap(parent) {
        var svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");

        svg.classList.add("hexmap")

        // hexagon shape variables
        var hex_di  = 100,
            // radius
            hex_rad = hex_di / 2,
            // apothem
            hex_apo = hex_rad * Math.cos(Math.PI / 6),
            // matrix defining state placement
            states_grid = this.usStateMatrix(),
            // data
            states_data = this.usStateData(),
            // rows we'll generate
            rows    = states_grid.length,
            // columns we'll generate
            cols    = states_grid[0].length,
            // stroke width around hexagon
            stroke  = 4,
            // the hover state zoom scale
            scale   = 2,
            // initial x
            x       = hex_rad * scale / 2 + stroke * scale,
            // initial y
            y       = hex_rad * scale + stroke * scale,
            // side length in pixels
            side    = Math.sin(Math.PI / 6) * hex_rad,
            // height of map in pixels
            height  = (hex_di - side) * rows + side + hex_rad * scale + stroke * scale,
            // width of map in pixels
            width   = (hex_apo * 2) * cols + hex_rad * scale + stroke * scale;
        

        // svg attributes
        svg.setAttribute("class", "svg");
        svg.setAttribute("width", "100%");
        svg.setAttribute("height", "100%");
        svg.setAttribute("viewBox", "0 0 " + width + " " + height);
        
        // loop variables
        var offset = false,
            // parsing state data
            states = states_data.states,
            // initial state index
            state_index = 0;

        let me = this;

        this.hexagons = []

        // draw grid
        for(var i = 0; i < states_grid.length; i++) {
            var loop_x = offset ? hex_apo * 2 : hex_apo;
            
            var loc_x = x; 
            for(var s = 0; s < states_grid[i].length; s++) {
                // grid plot in 0 and 1 array
                var grid_plot = states_grid[i][s];

                // if we have a plot in the grid
                if (grid_plot != 0) {
                    // get the state
                    var state = states[state_index];
                    
                    // create the hex group
                    var hexGroup = this.getHexGroup(svg, loc_x + loop_x , y, hex_rad, state, width);
                    
                    this.hexagons.push(hexGroup);
                    
                    // append the hex to our svg
                    svg.appendChild(hexGroup);
                    // increase the state index reference
                    state_index++;
                }

                // move our x plot to next hex position
                loc_x += hex_apo * 2; 
            }
            // move our y plot to next row position
            y += hex_di * 0.75; 
            // toggle offset per row
            offset = !offset;
        }

        // add svg to DOM
        $(parent).append(svg);

        this.svg = svg;
    }

    selectHexGroup(group){
        var elems = document.querySelectorAll(".hexstate");

        [].forEach.call(elems, function(el) {
            el.classList.remove("selected");
        });
        group.classList.add("selected");
    }

    // individual hex calculations
    getHexGroup(svg, x, y, r, state, width) {
        var svgNS  = svg.namespaceURI, // svgNS for creating svg elements
            group  = document.createElementNS(svgNS, "g"),
            hex    = document.createElementNS(svgNS, "polygon"),
            abbr   = document.createElementNS(svgNS, "text"),
            name   = document.createElementNS(svgNS, "text"),
            pi_six = Math.PI/6,
            cos_six = Math.cos(pi_six),
            sin_six = Math.sin(pi_six);

        // hexagon polygon points
        var hex_points = [
            [x, y - r].join(","),
            [x + cos_six * r, y - sin_six * r].join(","),
            [x + cos_six * r, y + sin_six * r].join(","),
            [x, y + r].join(","),
            [x - cos_six * r, y + sin_six * r].join(","),
            [x - cos_six * r, y - sin_six * r].join(",")
        ]
        
            
        hex.setAttribute("points", hex_points.join(" "));
        hex.style.webkitTransformOrigin = hex.style.transformOrigin = x + 'px ' + y + 'px';
        
        abbr.setAttribute("class", "state-abbr");
        abbr.setAttribute("x", x);
        abbr.setAttribute("y", y);
        abbr.textContent = state.abbr;
        
        group.appendChild(hex);  
        group.appendChild(abbr); 

        group.classList.add("hexstate");
        group.id = state.abbr;

        let me = this;
        group.addEventListener("click", (event)=>{me.selectHexGroup(group)})
        
        return group;
    }

    keyToName(str) {
        return str.replace(/_/g,' ')
            .replace(/\w\S*/g, function(txt) {
            return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
        });
    }

    usStateMatrix() {
        return [
            [1,0,0,0,0,0,0,0,0,0,0,1],
            [0,0,0,0,0,0,0,0,0,1,1,0],
            [0,1,1,1,1,1,0,1,0,1,1,1],
            [0,1,1,1,1,1,1,1,1,1,1,0],
            [0,1,1,1,1,1,1,1,1,1,1,0],
            [0,1,1,1,1,1,1,1,1,1,0,0],
            [0,0,0,1,1,1,1,1,1,0,0,0],
            [1,0,0,0,1,0,0,1,0,0,0,0]
        ]
    }

    usStateData() {
        return {
            states: [
            { abbr: "AK", name: "Alaska" },
            { abbr: "ME", name: "Maine"},

            { abbr: "VT", name: "Vermont" },
            { abbr: "NH", name: "New Hampshire"},

            { abbr: "WA", name: "Washington" },
            { abbr: "MT", name: "Montana" },
            { abbr: "ND", name: "North Dakota" },
            { abbr: "MN", name: "Minnesota" },
            { abbr: "WI", name: "Wisconsin" },
            { abbr: "MI", name: "Michigan" },
            { abbr: "NY", name: "New York" },
            { abbr: "MA", name: "Massachusetts" },
            { abbr: "RI", name: "Rhode Island"},

            { abbr: "ID", name: "Idaho" },
            { abbr: "WY", name: "Wyoming" },
            { abbr: "SD", name: "South Dakota" },
            { abbr: "IA", name: "Iowa" },
            { abbr: "IL", name: "Illinois" },
            { abbr: "IN", name: "Indiana" },
            { abbr: "OH", name: "Ohio" },
            { abbr: "PA", name: "Pennsylvania" },
            { abbr: "NJ", name: "New Jersey" },
            { abbr: "CT", name: "Connecticut"},

            { abbr: "OR", name: "Oregon" },
            { abbr: "NV", name: "Nevada" },
            { abbr: "CO", name: "Colorado" },
            { abbr: "NE", name: "Nebraska" },
            { abbr: "MO", name: "Missouri" },
            { abbr: "KY", name: "Kentucky" },
            { abbr: "WV", name: "West Virgina" },
            { abbr: "VA", name: "Virginia" },
            { abbr: "MD", name: "Maryland" },
            { abbr: "DE", name: "Delaware"},

            { abbr: "CA", name: "California" },
            { abbr: "UT", name: "Utah" },
            { abbr: "NM", name: "New Mexico" },
            { abbr: "KS", name: "Kansas" },
            { abbr: "AR", name: "Arkansas" },
            { abbr: "TN", name: "Tennessee" },
            { abbr: "NC", name: "North Carolina" },
            { abbr: "SC", name: "South Carolina" },
            { abbr: "DC", name: "District of Columbia"},

            { abbr: "AZ", name: "Arizona" },
            { abbr: "OK", name: "Oklahoma" },
            { abbr: "LA", name: "Louisiana" },
            { abbr: "MS", name: "Mississippi" },
            { abbr: "AL", name: "Alabama" },
            { abbr: "GA", name: "Georgia"},

            { abbr: "HI", name: "Hawaii" },
            { abbr: "TX", name: "Texas" },
            { abbr: "FL", name: "Florida" }
            ],
        }
    }

}

